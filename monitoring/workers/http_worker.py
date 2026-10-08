import asyncio
import httpx
from database import get_active_assets, save_monitoring_result, update_asset_status, create_event
from config import HTTP_ENDPOINTS

async def check_http_health(ip_address, endpoint="/health", port=80, timeout=3):
    """Check HTTP health endpoint"""
    url = f"http://{ip_address}:{port}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            response = await client.get(url)
            return True, response.status_code, response.elapsed.total_seconds() * 1000
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return False, None, None

async def check_asset_http(asset):
    """Check HTTP health on an application asset"""
    asset_id = asset['id']
    hostname = asset['hostname']
    ip_address = asset['ip_address']
    asset_type = asset['asset_type']
    
    endpoint = HTTP_ENDPOINTS.get(asset_type, "/")
    
    is_healthy, status_code, response_time = await check_http_health(ip_address, endpoint)
    
    if is_healthy:
        save_monitoring_result(
            asset_id=asset_id,
            check_type="HTTP",
            result="SUCCESS",
            response_time_ms=response_time,
            status_code=status_code,
            message=f"HTTP {status_code} - {response_time:.1f}ms"
        )
    else:
        save_monitoring_result(
            asset_id=asset_id,
            check_type="HTTP",
            result="FAILURE",
            status_code=status_code,
            message="HTTP check failed"
        )
        
        if asset['status'] == 'ONLINE':
            update_asset_status(asset_id, 'WARNING')
            create_event("MONITORING_CHECK", f"{hostname}: HTTP health check failed")
    
    return {
        "hostname": hostname,
        "healthy": is_healthy,
        "status_code": status_code,
        "response_time": response_time
    }

async def run_http_checks():
    """Run HTTP health checks on applications concurrently"""
    assets = get_active_assets()
    http_assets = [a for a in assets if a['asset_type'] in ['APPLICATION', 'NETWORK_SERVICE']]
    
    print(f"[HTTP] Checking {len(http_assets)} assets concurrently...")
    
    semaphore = asyncio.Semaphore(10)
    
    async def bounded_check(asset):
        async with semaphore:
            return await check_asset_http(asset)
    
    results = await asyncio.gather(*[bounded_check(a) for a in http_assets], return_exceptions=True)
    valid_results = [r for r in results if not isinstance(r, Exception)]
    
    healthy = sum(1 for r in valid_results if r['healthy'])
    print(f"[HTTP] Results: {healthy}/{len(valid_results)} healthy")
    return valid_results

if __name__ == "__main__":
    asyncio.run(run_http_checks())