import sqlite3

from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    hostname TEXT NOT NULL,
    run_name TEXT
);

CREATE TABLE IF NOT EXISTS samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(run_id),
    ts TEXT NOT NULL,
    metric TEXT NOT NULL,
    key TEXT NOT NULL, 
    value REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_samples_run_metric_ts 
    ON samples(run_id, metric, ts);

CREATE VIEW IF NOT EXISTS cpu_samples AS SELECT * FROM samples WHERE metric = 'cpu';
"""

def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(
        path,
        isolation_level=None,
        check_same_thread=False,
    )
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db(path: Path):
    conn = connect(path)
    conn.executescript(SCHEMA)
    conn.close()

