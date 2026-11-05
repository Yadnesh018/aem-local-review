"""The legacy invoicing service, as it runs in production.

Written in the standard library on purpose: it is the old system. Its quirks
are the specification the port must reproduce (see docs/legacy-behaviour.md).
"""

from __future__ import annotations

import argparse
import json
import re
from decimal import ROUND_HALF_UP, Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

from legacy.catalogue import PRODUCTS, VAT_RATES

CENT = Decimal("0.01")
_invoices: dict[str, dict] = {}
_counter = 0
_lock = Lock()


def money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def discount_percent(subtotal: Decimal) -> int:
    # Tiers on the subtotal before VAT; the threshold itself qualifies.
    if subtotal >= Decimal("5000"):
        return 10
    if subtotal >= Decimal("1000"):
        return 5
    return 0


def price_order(body: dict) -> tuple[int, dict]:
    lines = body.get("lines") or []
    if not lines:
        return 400, {"error": "empty_order"}
    country = str(body.get("country") or "").upper()
    if country not in VAT_RATES:
        return 422, {"error": "unsupported_country", "country": country}
    priced = []
    subtotal = Decimal("0")
    for index, line in enumerate(lines, start=1):
        sku = line.get("sku")
        quantity = line.get("quantity")
        if not isinstance(quantity, int) or quantity <= 0:
            return 400, {"error": "invalid_quantity", "line": index}
        product = PRODUCTS.get(sku)
        if product is None:
            return 404, {"error": "unknown_product", "sku": sku}
        unit = Decimal(product["price_cents"]) / 100
        line_total = (unit * quantity).quantize(CENT, rounding=ROUND_HALF_UP)
        subtotal += line_total
        priced.append({"sku": sku, "quantity": quantity, "unit_price": money(unit), "line_total": money(line_total)})
    percent = discount_percent(subtotal)
    discount = (subtotal * percent / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    taxable = subtotal - discount
    # VAT once, on the discounted subtotal, rounded half up.
    vat = (taxable * VAT_RATES[country] / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    return 200, {
        "country": country,
        "lines": priced,
        "subtotal": money(subtotal),
        "discount_percent": percent,
        "discount": money(discount),
        "vat_rate": VAT_RATES[country],
        "vat": money(vat),
        "total": money(taxable + vat),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:  # quiet
        pass

    def do_GET(self) -> None:
        if self.path == "/health":
            return self._send(200, {"status": "ok"})
        if self.path == "/products":
            return self._send(200, [PRODUCTS[k] | {"price": money(Decimal(PRODUCTS[k]["price_cents"]) / 100)}
                                    for k in sorted(PRODUCTS)])
        match = re.fullmatch(r"/invoices/(INV-\d{6})", self.path)
        if match:
            invoice = _invoices.get(match.group(1))
            return self._send(200, invoice) if invoice else self._send(404, {"error": "not_found"})
        return self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:
        global _counter
        if self.path != "/invoices":
            return self._send(404, {"error": "not_found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "malformed_body"})
        status, payload = price_order(body)
        if status != 200:
            return self._send(status, payload)
        with _lock:
            _counter += 1
            number = f"INV-{_counter:06d}"
            invoice = {"number": number, **payload}
            _invoices[number] = invoice
        return self._send(201, invoice)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
