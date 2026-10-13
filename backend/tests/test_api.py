import time

from sqlmodel import select

from backend.api import products as products_api
from backend.auth import ensure_demo_user
from backend.models import AccessRequest, Offer, PriceSnapshot, Product
from backend.tests.conftest import make_user, session_scope


def add_product(user_id: int) -> tuple[int, int]:
    with session_scope() as session:
        product = Product(user_id=user_id, name="Desk lamp", currency="EUR")
        session.add(product)
        session.flush()
        offer = Offer(
            product_id=product.id,
            store="rival.de",
            domain="rival.de",
            url="https://rival.de/lamp",
            status="proposed",
            last_price=80.0,
            currency="EUR",
            match_confidence=0.9,
            match_reason="Same EAN.",
        )
        session.add(offer)
        session.flush()
        session.add(
            PriceSnapshot(
                offer_id=offer.id,
                price=80.0,
                currency="EUR",
                method="jsonld",
                fetched_via="direct",
                evidence='{"price":80}',
            )
        )
        session.commit()
        return product.id, offer.id


def test_anonymous_visitor_sees_read_only_demo(client):
    with session_scope() as session:
        demo = ensure_demo_user(session)
    add_product(demo.id)

    assert client.get("/api/auth/me").json() == {"email": None, "demo": True}
    listed = client.get("/api/products").json()
    assert listed and listed[0]["name"] == "Desk lamp"

    response = client.post("/api/products", json={"url": "https://shop.example.com/p"})
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "demo_read_only"


def test_login_logout_and_errors(client, user):
    bad = client.post("/api/auth/login", json={"email": user.email, "password": "nope"})
    assert bad.status_code == 401 and bad.json()["detail"]["code"] == "bad_credentials"

    ok = client.post(
        "/api/auth/login", json={"email": user.email.upper(), "password": "secret-pass"}
    )
    assert ok.status_code == 200
    assert client.get("/api/auth/me").json() == {"email": user.email, "demo": False}

    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").json()["demo"] is True


def test_validation_errors_are_readable(logged_in):
    response = logged_in.post("/api/products", json={})
    assert response.status_code == 422
    assert response.json()["detail"] == {"code": "invalid_input", "message": "url: Field required"}


def test_agent_needs_api_keys(logged_in):
    response = logged_in.post("/api/products", json={"url": "https://shop.example.com/p"})
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "not_configured"


def test_products_are_private_to_their_owner(logged_in):
    stranger = make_user()
    product_id, _ = add_product(stranger.id)
    assert logged_in.get(f"/api/products/{product_id}").status_code == 404


def test_approve_offer_and_product_detail(logged_in, user):
    product_id, offer_id = add_product(user.id)
    detail = logged_in.get(f"/api/products/{product_id}").json()
    assert detail["offers"][0]["status"] == "proposed"
    assert detail["offers"][0]["latest"]["evidence"] == '{"price":80}'

    approved = logged_in.patch(f"/api/offers/{offer_id}", json={"status": "tracking"}).json()
    assert approved["status"] == "tracking" and approved["next_check_at"] is not None

    history = logged_in.get(f"/api/products/{product_id}/history").json()
    assert history[0]["points"][0]["price"] == 80.0
    assert logged_in.delete(f"/api/products/{product_id}").status_code == 204
    assert logged_in.get(f"/api/products/{product_id}").status_code == 404


def test_add_competitor_link_rejects_private_urls(logged_in, user, monkeypatch):
    product_id, _ = add_product(user.id)
    started = []
    monkeypatch.setattr(products_api, "spawn", lambda coro, name: started.append(coro.close()))

    bad = logged_in.post(f"/api/products/{product_id}/offers", json={"url": "http://127.0.0.1/x"})
    assert bad.status_code == 400 and bad.json()["detail"]["code"] == "bad_url"

    good = logged_in.post(f"/api/products/{product_id}/offers", json={"url": "93.184.215.14/lamp"})
    assert good.status_code == 201, good.text
    assert good.json()["source"] == "manual" and len(started) == 1


def test_access_request_and_honeypot(client):
    body = {"name": "Ann", "email": "ann@shop.example.com", "message": "Interested"}
    assert client.post("/api/access-requests", json=body).status_code == 201
    assert client.post("/api/access-requests", json=body | {"website": "spam"}).status_code == 201
    with session_scope() as session:
        stored = session.exec(select(AccessRequest).where(AccessRequest.name == "Ann")).all()
    assert len(stored) == 1  # the bot submission was silently dropped


def test_health_reports_components(client):
    health = client.get("/api/health").json()
    assert health["status"] == "ok" and health["database"] == "ok"
    assert health["ai"] is False and health["scheduler"]["status"] == "stopped"


def test_background_runs_start_from_the_api(logged_in, user, monkeypatch):
    """Runs are started with the real `spawn` (this used to fail in sync endpoints)."""
    product_id, _ = add_product(user.id)

    async def fake_discovery(run, *, url=None, product_id=None):
        run.finish(summary="fake discovery")

    async def fake_check(product_id, run, offer_ids=None):
        return "fake check"

    monkeypatch.setattr(products_api, "run_discovery", fake_discovery)
    monkeypatch.setattr("backend.scheduler.monitor.check_product", fake_check)

    for path in (f"/api/products/{product_id}/discover", f"/api/products/{product_id}/check"):
        response = logged_in.post(path)
        assert response.status_code == 202, response.text
        run_id = response.json()["run_id"]
        for _ in range(50):
            run = logged_in.get(f"/api/runs/{run_id}").json()
            if run["status"] != "running":
                break
            time.sleep(0.02)
        assert run["status"] == "completed" and run["summary"].startswith("fake")
