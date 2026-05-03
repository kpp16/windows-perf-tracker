import platform

from collector import collect
from pathlib import Path

from db import init_db, connect

DB_PATH = Path("perf.db")

def main():
    init_db(DB_PATH)
    conn = connect(DB_PATH)
    
    collect(conn=conn, hostname=platform.node())

if __name__ == "__main__":
    main()
