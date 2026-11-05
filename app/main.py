"""The target service. Products are ported; invoices are the open story (docs/STORY.md)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import db
from app.money import as_text, from_cents


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Invoicing (port)", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/products")
def list_products() -> list[dict]:
    with db.connect() as connection:
        return [
            {"sku": row["sku"], "name": row["name"], "price_cents": row["price_cents"],
             "price": as_text(from_cents(row["price_cents"]))}
            for row in db.products(connection)
        ]
