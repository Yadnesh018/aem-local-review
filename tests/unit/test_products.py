from fastapi.testclient import TestClient


def test_products_are_listed_by_sku(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("app.db.DB_PATH", str(tmp_path / "t.db"))
    from app.main import app

    with TestClient(app) as client:
        body = client.get("/products").json()
    assert [p["sku"] for p in body] == ["CHAIR-01", "DESK-02", "LAMP-03", "MAT-04"]
    assert body[0]["price"] == "129.99"
