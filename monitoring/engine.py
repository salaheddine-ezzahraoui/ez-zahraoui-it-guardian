import asyncio
import signal
import sys
import traceback
from datetime import datetime
from workers.icmp_worker import run_icmp_checks
from workers.tcp_worker import run_tcp_checks
from workers.http_worker import run_http_checks
from database import create_event
from config import MONITORING_INTERVAL_SECONDS

class MonitoringEngine:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        print("\n[ENGINE] Shutting down monitoring engine...")
        self.running = False
    
    async def run_check_cycle(self):
        """Run one complete monitoring cycle"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"[ENGINE] Starting monitoring cycle at {timestamp}")
        print(f"{'='*60}")
        
        try:
            create_event("MONITORING_CHECK", "Monitoring cycle started")
        except Exception as e:
            print(f"[ENGINE] Failed to create event: {e}")
        
        try:
            # Run all checks concurrently
            icmp_task = asyncio.create_task(run_icmp_checks())
            tcp_task = asyncio.create_task(run_tcp_checks())
            http_task = asyncio.create_task(run_http_checks())
            
            # Wait for all to complete
            await asyncio.gather(icmp_task, tcp_task, http_task, return_exceptions=True)
            
        except Exception as e:
            print(f"[ENGINE] Error in monitoring cycle: {e}")
            traceback.print_exc()
        
        print(f"[ENGINE] Monitoring cycle completed at {datetime.now().strftime('%H:%M:%S')}")
    
    async def run(self):
        """Main loop"""
        print(f"""
============================================================
        EZ-ZAHRAOUI IT Guardian Monitoring Engine
============================================================
  Interval: {MONITORING_INTERVAL_SECONDS}s  |  Checks: ICMP, TCP, HTTP
============================================================
        """)
        
        try:
            create_event("SYSTEM", "Monitoring engine started")
        except Exception as e:
            print(f"[ENGINE] Failed to create event: {e}")
        
        while self.running:
            await self.run_check_cycle()
            
            if self.running:
                print(f"[ENGINE] Waiting {MONITORING_INTERVAL_SECONDS}s until next cycle...")
                try:
                    await asyncio.wait_for(
                        self.wait_for_shutdown(),
                        timeout=MONITORING_INTERVAL_SECONDS
                    )
                except asyncio.TimeoutError:
                    continue
    
    async def wait_for_shutdown(self):
        """Wait until shutdown is requested"""
        while self.running:
            await asyncio.sleep(1)

if __name__ == "__main__":
    engine = MonitoringEngine()
    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        print("\n[ENGINE] Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ENGINE] Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
