from datetime import datetime
import logging
import sqlite3
import threading
from timer import RepeatedTimer
from stats import CPUStats, DiskStats, RAMStats

logger = logging.getLogger(__name__)

def collect(conn: sqlite3.Connection, hostname: str, *args, **kwargs):
    cur = conn.execute(
        "INSERT INTO runs(started_at, hostname) VALUES (?, ?)",
        (datetime.now().isoformat(), hostname)
    )
    run_id = cur.lastrowid or 0
    conn.commit()

    cpu_stats = CPUStats(conn=conn, run_id=run_id)
    ram_stats = RAMStats(conn=conn, run_id=run_id)
    disk_stats = DiskStats(conn=conn, run_id=run_id)
    
    timer_cpu = RepeatedTimer(interval=1.0, function=cpu_stats.collect)
    timer_ram = RepeatedTimer(interval=1.0, function=ram_stats.collect)
    timer_disk = RepeatedTimer(interval=1.0, function=disk_stats.collect)
    
    stop_event = threading.Event()
    
    timer_cpu.start()
    timer_ram.start()
    timer_disk.start()
    
    logger.info("Collecting... press Ctr+C to stop") 

    try:
        while True:
            stop_event.wait(timeout=0.5)
    except KeyboardInterrupt:
        print("\nStopping...")
        
        timer_cpu.stop()
        timer_disk.stop()
        timer_ram.stop()
        
        conn.execute(
            "UPDATE runs SET ended_at = ? WHERE run_id = ?",
            (datetime.now().isoformat(), run_id)
        )
        conn.commit()
        conn.close()
    
    