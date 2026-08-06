import json
import logging
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote_plus

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

from . import APP_VERSION
from .database import SessionLocal
from .models import Address, Contact, PhoneNumber
from .validation import address_values, contact_values, phone_values


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"level": record.levelname.lower(), "event": record.getMessage(), "service": "address-book", "version": APP_VERSION})


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("address_book")
logger.handlers = [handler]
logger.setLevel(logging.INFO)
logger.propagate = False

BASE = Path(__file__).parent
app = FastAPI(title="SCS323 Address Book", version=APP_VERSION, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def redirect(path: str, message: str = "") -> RedirectResponse:
    suffix = f"?message={quote_plus(message)}" if message else ""
    return RedirectResponse(f"{path}{suffix}", status_code=303)


def get_contact(session, contact_id: int) -> Contact:
    item = session.scalar(select(Contact).where(Contact.id == contact_id).options(selectinload(Contact.addresses), selectinload(Contact.phone_numbers)))
    if item is None: raise HTTPException(404, "Contact not found")
    return item


def detail_context(contact: Contact, message: str = "", **overrides) -> dict:
    context = {
        "contact": contact,
        "message": message,
        "address_errors": {},
        "address_values": {},
        "phone_errors": {},
        "phone_values": {},
        "version": APP_VERSION,
    }
    context.update(overrides)
    return context


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "address-book", "version": APP_VERSION}


@app.get("/ready")
def ready() -> dict[str, str]:
    try:
        with session_scope() as session: session.execute(text("SELECT 1"))
        return {"status": "ready", "service": "address-book", "version": APP_VERSION}
    except SQLAlchemyError as exc:
        logger.warning("readiness.database_unavailable")
        raise HTTPException(503, "Database is not ready") from exc


@app.get("/", response_class=HTMLResponse)
def contact_list(request: Request, q: str = "", message: str = ""):
    with session_scope() as session:
        query = select(Contact).order_by(Contact.last_name, Contact.first_name)
        if q.strip():
            term = f"%{q.strip()}%"
            query = query.where(or_(Contact.first_name.ilike(term), Contact.last_name.ilike(term), Contact.email.ilike(term)))
        contacts = list(session.scalars(query))
    return templates.TemplateResponse(request, "index.html", {"contacts": contacts, "q": q.strip(), "message": message, "version": APP_VERSION})


@app.get("/contacts/new", response_class=HTMLResponse)
def new_contact(request: Request):
    return templates.TemplateResponse(request, "contact_form.html", {"contact": {}, "errors": {}, "mode": "Create", "version": APP_VERSION})


@app.post("/contacts/new", response_class=HTMLResponse)
def create_contact(request: Request, first_name: str = Form(""), last_name: str = Form(""), email: str = Form("")):
    values, errors = contact_values(first_name, last_name, email)
    if errors: return templates.TemplateResponse(request, "contact_form.html", {"contact": values, "errors": errors, "mode": "Create", "version": APP_VERSION}, status_code=422)
    with session_scope() as session:
        item = Contact(**values); session.add(item)
        try: session.commit()
        except IntegrityError:
            session.rollback(); errors["email"] = "That email address already belongs to a contact."
            return templates.TemplateResponse(request, "contact_form.html", {"contact": values, "errors": errors, "mode": "Create", "version": APP_VERSION}, status_code=409)
        logger.info("contact.created")
        return redirect(f"/contacts/{item.id}", "Contact created.")


@app.get("/contacts/{contact_id}", response_class=HTMLResponse)
def contact_detail(request: Request, contact_id: int, message: str = ""):
    with session_scope() as session: item = get_contact(session, contact_id)
    return templates.TemplateResponse(request, "contact_detail.html", detail_context(item, message))


@app.get("/contacts/{contact_id}/edit", response_class=HTMLResponse)
def edit_contact(request: Request, contact_id: int):
    with session_scope() as session: item = get_contact(session, contact_id)
    return templates.TemplateResponse(request, "contact_form.html", {"contact": item, "errors": {}, "mode": "Edit", "version": APP_VERSION})


@app.post("/contacts/{contact_id}/edit", response_class=HTMLResponse)
def update_contact(request: Request, contact_id: int, first_name: str = Form(""), last_name: str = Form(""), email: str = Form("")):
    values, errors = contact_values(first_name, last_name, email)
    if errors: return templates.TemplateResponse(request, "contact_form.html", {"contact": {"id": contact_id, **values}, "errors": errors, "mode": "Edit", "version": APP_VERSION}, status_code=422)
    with session_scope() as session:
        item = get_contact(session, contact_id)
        for key, value in values.items(): setattr(item, key, value)
        try: session.commit()
        except IntegrityError:
            session.rollback(); errors["email"] = "That email address already belongs to a contact."
            return templates.TemplateResponse(request, "contact_form.html", {"contact": {"id": contact_id, **values}, "errors": errors, "mode": "Edit", "version": APP_VERSION}, status_code=409)
    logger.info("contact.updated")
    return redirect(f"/contacts/{contact_id}", "Contact updated.")


@app.get("/contacts/{contact_id}/delete", response_class=HTMLResponse)
def delete_confirm(request: Request, contact_id: int):
    with session_scope() as session: item = get_contact(session, contact_id)
    return templates.TemplateResponse(request, "delete_confirm.html", {"contact": item, "version": APP_VERSION})


@app.post("/contacts/{contact_id}/delete")
def delete_contact(contact_id: int):
    with session_scope() as session:
        item = get_contact(session, contact_id); session.delete(item); session.commit()
    logger.info("contact.deleted")
    return redirect("/", "Contact deleted.")


@app.post("/contacts/{contact_id}/addresses", response_class=HTMLResponse)
def add_address(request: Request, contact_id: int, street: str = Form(""), city: str = Form(""), state: str = Form(""), postal_code: str = Form(""), address_type: str = Form("")):
    values, errors = address_values(street, city, state, postal_code, address_type)
    if errors:
        with session_scope() as session: item = get_contact(session, contact_id)
        return templates.TemplateResponse(request, "contact_detail.html", detail_context(item, address_errors=errors, address_values=values), status_code=422)
    with session_scope() as session: get_contact(session, contact_id); session.add(Address(contact_id=contact_id, **values)); session.commit()
    logger.info("address.created")
    return redirect(f"/contacts/{contact_id}", "Address added.")


@app.post("/contacts/{contact_id}/addresses/{address_id}/delete")
def remove_address(contact_id: int, address_id: int):
    with session_scope() as session:
        item = session.scalar(select(Address).where(Address.id == address_id, Address.contact_id == contact_id))
        if item is None: raise HTTPException(404, "Address not found")
        session.delete(item); session.commit()
    logger.info("address.deleted")
    return redirect(f"/contacts/{contact_id}", "Address removed.")


@app.post("/contacts/{contact_id}/phones", response_class=HTMLResponse)
def add_phone(request: Request, contact_id: int, phone_number: str = Form(""), phone_type: str = Form("")):
    values, errors = phone_values(phone_number, phone_type)
    if errors:
        with session_scope() as session: item = get_contact(session, contact_id)
        return templates.TemplateResponse(request, "contact_detail.html", detail_context(item, phone_errors=errors, phone_values=values), status_code=422)
    with session_scope() as session: get_contact(session, contact_id); session.add(PhoneNumber(contact_id=contact_id, **values)); session.commit()
    logger.info("phone.created")
    return redirect(f"/contacts/{contact_id}", "Phone number added.")


@app.post("/contacts/{contact_id}/phones/{phone_id}/delete")
def remove_phone(contact_id: int, phone_id: int):
    with session_scope() as session:
        item = session.scalar(select(PhoneNumber).where(PhoneNumber.id == phone_id, PhoneNumber.contact_id == contact_id))
        if item is None: raise HTTPException(404, "Phone number not found")
        session.delete(item); session.commit()
    logger.info("phone.deleted")
    return redirect(f"/contacts/{contact_id}", "Phone number removed.")
