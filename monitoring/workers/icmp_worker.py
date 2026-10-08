import asyncio
import platform
import time
from datetime import datetime
from database import get_active_assets, save_monitoring_result, update_asset_status, create_event, create_incident
from config import MONITORING_TIMEOUT_SECONDS, MONITORING_PING_COUNT

async def ping_host(ip_address, timeout=2, count=2):
    """Ping a host and return (success, response_time_ms, packet_loss_percent)"""
    system = platform.system().lower()
    
    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), ip_address]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), ip_address]
    
    try:
        start_time = time.time()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout * count + 2)
        elapsed = (time.time() - start_time) * 1000
        
        output = stdout.decode('utf-8', errors='ignore')
        
        if system == "windows":
            if "TTL=" in output or "ttl=" in output:
                times = []
                for line in output.split('\n'):
                    if 'time=' in line or 'time<' in line:
                        try:
                            if 'time=' in line:
                                t = line.split('time=')[1].split('ms')[0]
                            else:
                                t = line.split('time<')[1].split('ms')[0]
                            times.append(float(t))
                        except:
                            pass
                
                avg_time = sum(times) / len(times) if times else elapsed / count
                sent = count
                received = len(times)
                packet_loss = ((sent - received) / sent) * 100 if sent > 0 else 0
                return True, avg_time, packet_loss
            else:
                return False, None, 100.0
        else:
            if " 0% packet loss" in output or " 0.0% packet loss" in output:
                avg_time = elapsed / count
                return True, avg_time, 0.0
            elif "packet loss" in output:
                for line in output.split('\n'):
                    if 'packet loss' in line:
                        try:
                            loss_str = line.split('%')[0].split()[-1]
                            packet_loss = float(loss_str)
                        except:
                            packet_loss = 100.0
                        if packet_loss < 100:
                            avg_time = elapsed / count
                            return True, avg_time, packet_loss
                        else:
                            return False, None, 100.0
                return False, None, 100.0
            else:
                return False, None, 100.0
                
    except asyncio.TimeoutError:
        return False, None, 100.0
    except Exception as e:
        return False, None, 100.0

async def check_asset_icmp(asset):
    """Check a single asset with ICMP ping"""
    asset_id = asset['id']
    hostname = asset['hostname']
    ip_address = asset['ip_address']
    
    success, response_time, packet_loss = await ping_host(
        ip_address, 
        timeout=MONITORING_TIMEOUT_SECONDS,
        count=MONITORING_PING_COUNT
    )
    
    if success:
        result = "SUCCESS"
        message = f"Ping OK - {response_time:.1f}ms"
        if packet_loss and packet_loss > 10:
            new_status = "WARNING"
            message += f" (packet loss: {packet_loss:.1f}%)"
        else:
            new_status = "ONLINE"
    else:
        result = "TIMEOUT"
        new_status = "OFFLINE"
        message = "Ping timeout - host unreachable"
        response_time = None
        packet_loss = 100.0
    
    save_monitoring_result(
        asset_id=asset_id,
        check_type="ICMP",
        result=result,
        response_time_ms=response_time,
        packet_loss=packet_loss,
        message=message
    )
    
    old_status = asset['status']
    update_asset_status(asset_id, new_status)
    
    if old_status != new_status:
        if new_status == "OFFLINE":
            create_event("MONITORING_CHECK", f"{hostname} is OFFLINE (ping timeout)")
            if asset['criticality'] in ['CRITICAL', 'HIGH']:
                severity = "CRITICAL" if asset['criticality'] == "CRITICAL" else "HIGH"
                priority = "P1" if asset['criticality'] == "CRITICAL" else "P2"
                create_incident(asset_id, "NETWORK", severity, priority,
                    f"{hostname} is offline",
                    f"{hostname} ({ip_address}) is not responding to ping checks.")
        elif new_status == "WARNING":
            create_event("MONITORING_CHECK", f"{hostname} WARNING - packet loss detected")
        elif new_status == "ONLINE" and old_status == "OFFLINE":
            create_event("MONITORING_CHECK", f"{hostname} is back ONLINE")
    
    return {
        "hostname": hostname,
        "status": new_status,
        "response_time": response_time,
        "packet_loss": packet_loss
    }

async def run_icmp_checks():
    """Run ICMP checks on all active assets concurrently"""
    assets = get_active_assets()
    print(f"[ICMP] Checking {len(assets)} assets concurrently...")
    
    # Run all checks concurrently with a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(20)
    
    async def bounded_check(asset):
        async with semaphore:
            return await check_asset_icmp(asset)
    
    results = await asyncio.gather(*[bounded_check(a) for a in assets], return_exceptions=True)
    
    # Filter out exceptions
    valid_results = [r for r in results if not isinstance(r, Exception)]
    errors = [r for r in results if isinstance(r, Exception)]
    
    online = sum(1 for r in valid_results if r['status'] == 'ONLINE')
    offline = sum(1 for r in valid_results if r['status'] == 'OFFLINE')
    warning = sum(1 for r in valid_results if r['status'] == 'WARNING')
    
    print(f"[ICMP] Results: {online} online, {warning} warning, {offline} offline")
    if errors:
        print(f"[ICMP] {len(errors)} errors occurred")
    return valid_results

if __name__ == "__main__":
    asyncio.run(run_icmp_checks())