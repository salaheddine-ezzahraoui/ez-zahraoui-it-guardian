import asyncio
import time
from database import get_active_assets, save_monitoring_result, update_asset_status, create_event
from config import TCP_PORTS

async def check_tcp_port(ip_address, port, timeout=3):
    """Check if a TCP port is open"""
    try:
        start_time = time.time()
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip_address, port),
            timeout=timeout
        )
        elapsed = (time.time() - start_time) * 1000
        writer.close()
        await writer.wait_closed()
        return True, elapsed
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return False, None

async def check_asset_tcp(asset):
    """Check TCP ports on a server asset"""
    asset_id = asset['id']
    hostname = asset['hostname']
    ip_address = asset['ip_address']
    asset_type = asset['asset_type']
    
    ports = TCP_PORTS.get(asset_type, TCP_PORTS.get('SERVER', []))
    
    open_ports = []
    closed_ports = []
    
    for port in ports:
        is_open, response_time = await check_tcp_port(ip_address, port)
        if is_open:
            open_ports.append(port)
            save_monitoring_result(
                asset_id=asset_id,
                check_type="TCP",
                result="SUCCESS",
                response_time_ms=response_time,
                status_code=port,
                message=f"Port {port} open"
            )
        else:
            closed_ports.append(port)
            save_monitoring_result(
                asset_id=asset_id,
                check_type="TCP",
                result="FAILURE",
                status_code=port,
                message=f"Port {port} closed"
            )
    
    critical_ports = [p for p in closed_ports if p in [80, 443, 3389]]
    if critical_ports and asset['status'] == 'ONLINE':
        update_asset_status(asset_id, 'WARNING')
        create_event("MONITORING_CHECK", f"{hostname}: Critical ports closed: {critical_ports}")
    
    return {
        "hostname": hostname,
        "open_ports": open_ports,
        "closed_ports": closed_ports
    }

async def run_tcp_checks():
    """Run TCP checks on servers and network services concurrently"""
    assets = get_active_assets()
    tcp_assets = [a for a in assets if a['asset_type'] in ['SERVER', 'NETWORK_SERVICE', 'APPLICATION']]
    
    print(f"[TCP] Checking {len(tcp_assets)} assets concurrently...")
    
    semaphore = asyncio.Semaphore(10)
    
    async def bounded_check(asset):
        async with semaphore:
            return await check_asset_tcp(asset)
    
    results = await asyncio.gather(*[bounded_check(a) for a in tcp_assets], return_exceptions=True)
    valid_results = [r for r in results if not isinstance(r, Exception)]
    
    print(f"[TCP] Completed checks on {len(valid_results)} assets")
    return valid_results

if __name__ == "__main__":
    asyncio.run(run_tcp_checks())