import psutil
import sqlite3

from datetime import datetime
from enum import Enum, auto

class StatType(Enum):
    CPU = auto()
    GPU = auto()
    RAM = auto()
    SSD = auto()
    POWER = auto()
    DISK = auto()

class BaseStats:
    def __init__(self, type: Enum, run_id: int, conn: sqlite3.Connection):
        self.type = type
        self.conn = conn
        self.run_id = run_id
        self.stats: dict[str, float | int] = {} 

    def to_text(self):
        print(f"---{self.type.name}---")
        for stat, value in self.stats.items():
            print(f"{stat}: {value}")

    def to_db(self):
        if not self.stats:
            return

        ts = datetime.now().isoformat()
        metric = self.type.name.lower()
        rows = [
            (self.run_id, ts, metric, key, float(value))
            for key, value in self.stats.items()
        ]

        with self.conn:
            self.conn.executemany(
                "INSERT INTO samples (run_id, ts, metric, key, value) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            self.conn.commit()
        
    def collect(self, *args, **kwargs) -> None:
        raise NotImplementedError 

class CPUStats(BaseStats):
    def __init__(self, run_id: int, conn: sqlite3.Connection):
        super().__init__(StatType.CPU, run_id, conn)
        
        num_cores = psutil.cpu_count(logical=False)
        num_logical_cores = psutil.cpu_count(logical=True)

        self.stats["num_cores"] = num_cores or 0
        self.stats["num_logical_cores"] = num_logical_cores or 0

    def collect(self, *args, **kwargs):
        cores_pct = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_freq_overall = psutil.cpu_freq()
        cpu_freq_per_cpu = psutil.cpu_freq(percpu=True)

        overall_current = cpu_freq_overall.current
        overall_min = cpu_freq_overall.min
        overall_max = cpu_freq_overall.max

        self.stats["freq_overall_current"] = overall_current
        self.stats["freq_overall_min"] = overall_min
        self.stats["freq_overall_max"] = overall_max

        for idx, core_freq in enumerate(cpu_freq_per_cpu):
            core_current = core_freq.current
            core_min = core_freq.min
            core_max = core_freq.max

            self.stats[f"freq_core_{idx}_current"] = core_current
            self.stats[f"freq_core_{idx}_min"] = core_min
            self.stats[f"freq_core_{idx}_max"] = core_max

        for idx, core_pct in enumerate(cores_pct):
           self.stats[f"CPU {idx}"] = core_pct

        self.to_db()
        self.to_text()


class RAMStats(BaseStats):
    def __init__(self, run_id: int, conn: sqlite3.Connection):
        super().__init__(StatType.RAM, run_id, conn)

    def collect(self, *args, **kwargs):
        mem = psutil.virtual_memory()

        self.stats["total_ram"] = mem.total
        self.stats["available_ram"] = mem.available
        self.stats["ram_pct"] = mem.percent
        self.stats["ram_used"] = mem.used
        self.stats["ram_free"] = mem.free

        self.to_db()
        self.to_text()


class DiskStats(BaseStats):
    def __init__(self, run_id: int, conn: sqlite3.Connection):
        super().__init__(StatType.DISK, run_id, conn)

    def collect(self, *args, **kwargs):
        disk_usage = psutil.disk_usage('/')

        self.stats["disk_total"] = disk_usage.total
        self.stats["disk_used"] = disk_usage.used
        self.stats["disk_free"] = disk_usage.free
        self.stats["disk_pct"] = disk_usage.percent

        self.to_db()
        self.to_text()
