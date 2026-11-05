"""The target service: products, and invoice creation and retrieval."""

from __future__ import annotations

from contextlib import asynccontextmanager
from json import JSONDecodeError

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import db
from app.money import as_text, from_cents
from app.pricing import Refusal, price


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


@app.post("/invoices")
async def create_invoice(request: Request) -> JSONResponse:
    try:
        order = await request.json()
    except (JSONDecodeError, UnicodeDecodeError):
        return JSONResponse({"error": "malformed_body"}, status_code=400)
    with db.connect() as connection:
        try:
            invoice = price(order, lambda sku: db.product(connection, sku))
        except Refusal as refusal:
            return JSONResponse(refusal.body, status_code=refusal.status)
        return JSONResponse(db.save_invoice(connection, invoice), status_code=201)


@app.get("/invoices/{number}")
def read_invoice(number: str) -> JSONResponse:
    with db.connect() as connection:
        invoice = db.get_invoice(connection, number)
    if invoice is None:
        return JSONResponse({"error": "not_found"}, status_code=404)
    return JSONResponse(invoice)
