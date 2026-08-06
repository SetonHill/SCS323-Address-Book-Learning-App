from fastapi.testclient import TestClient
from sqlalchemy import delete
from urllib.parse import urlparse

from app.database import SessionLocal
from app.main import app
from app.models import Contact

client = TestClient(app)


def clear_contacts():
    with SessionLocal() as session:
        session.execute(delete(Contact)); session.commit()


def test_health_and_readiness_include_version():
    assert client.get("/health").json() == {"status": "ok", "service": "address-book", "version": "1.0.0"}
    assert client.get("/ready").json()["status"] == "ready"


def test_complete_contact_address_phone_search_edit_delete_flow():
    clear_contacts()
    created = client.post("/contacts/new", data={"first_name": "Taylor", "last_name": "Ng", "email": "taylor.ng@example.test"}, follow_redirects=False)
    assert created.status_code == 303
    location = created.headers["location"]
    detail = client.get(location)
    assert "Taylor Ng" in detail.text
    contact_id = int(urlparse(location).path.split("/")[2])
    assert client.post(f"/contacts/{contact_id}/addresses", data={"street": "75 Maple Drive", "city": "Greensburg", "state": "PA", "postal_code": "15601", "address_type": "home"}).status_code == 200
    assert client.post(f"/contacts/{contact_id}/phones", data={"phone_number": "724-555-0199", "phone_type": "mobile"}).status_code == 200
    found = client.get("/?q=Taylor")
    assert "taylor.ng@example.test" in found.text
    edited = client.post(f"/contacts/{contact_id}/edit", data={"first_name": "Taylor", "last_name": "Nguyen", "email": "taylor.ng@example.test"}, follow_redirects=True)
    assert "Taylor Nguyen" in edited.text
    deleted = client.post(f"/contacts/{contact_id}/delete", follow_redirects=True)
    assert "Contact deleted" in deleted.text and "No contacts yet" in deleted.text


def test_duplicate_email_returns_safe_validation_message():
    clear_contacts()
    payload = {"first_name": "Avery", "last_name": "Morgan", "email": "avery@example.test"}
    assert client.post("/contacts/new", data=payload).status_code == 200
    response = client.post("/contacts/new", data=payload)
    assert response.status_code == 409
    assert "already belongs to a contact" in response.text
    assert "Traceback" not in response.text
