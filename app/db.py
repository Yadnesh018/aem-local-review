"""SQLite storage. Every query is parameterised (guardrail: no SQL built by concatenation)."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator

DB_PATH = os.environ.get("APP_DB", "invoicing.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL
);
"""

SEED = [
    ("CHAIR-01", "Office chair", 12999),
    ("DESK-02", "Standing desk", 49950),
    ("LAMP-03", "Desk lamp", 2495),
    ("MAT-04", "Floor mat", 3333),
]


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with connect() as db:
        db.executescript(SCHEMA)
        db.executemany("INSERT OR IGNORE INTO products (sku, name, price_cents) VALUES (?, ?, ?)", SEED)


def product(db: sqlite3.Connection, sku: str) -> sqlite3.Row | None:
    return db.execute("SELECT sku, name, price_cents FROM products WHERE sku = ?", (sku,)).fetchone()


def products(db: sqlite3.Connection) -> list[sqlite3.Row]:
    return db.execute("SELECT sku, name, price_cents FROM products ORDER BY sku").fetchall()
