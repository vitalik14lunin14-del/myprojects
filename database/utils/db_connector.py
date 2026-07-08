import sqlite3
from contextlib import contextmanager
from typing import Generator

@contextmanager
def create_transaction(db_path: str, tuning: bool = False) -> Generator[sqlite3.Cursor, None, None]:
    conn = sqlite3.connect(db_path)
    if tuning:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=-2000000;")
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@contextmanager
def create_connection(db_path: str, tuning: bool = False) -> Generator[sqlite3.Connection, None, None]:
    con = sqlite3.connect(db_path)
    if tuning:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
        con.execute("PRAGMA cache_size=-2000000;")
    try:
        yield con
    finally:
        con.close()