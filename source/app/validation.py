import re

from email_validator import EmailNotValidError, validate_email

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'-]{0,79}$")
PHONE_RE = re.compile(r"^[0-9()+. -]{7,30}$")
POSTAL_RE = re.compile(r"^[0-9]{5}(?:-[0-9]{4})?$")


def contact_values(first_name: str, last_name: str, email: str) -> tuple[dict[str, str], dict[str, str]]:
    values = {"first_name": first_name.strip(), "last_name": last_name.strip(), "email": email.strip()}
    errors: dict[str, str] = {}
    for field in ("first_name", "last_name"):
        if not NAME_RE.fullmatch(values[field]):
            errors[field] = "Use 1–80 letters plus ordinary name punctuation."
    try:
        # The example deliberately uses the reserved `.test` domain so students
        # never email a real person while exercising forms and database flows.
        values["email"] = validate_email(values["email"], check_deliverability=False, test_environment=True).normalized
    except EmailNotValidError:
        errors["email"] = "Enter a complete email address such as alex@example.test."
    return values, errors


def address_values(street: str, city: str, state: str, postal_code: str, address_type: str) -> tuple[dict[str, str], dict[str, str]]:
    values = {"street": street.strip(), "city": city.strip(), "state": state.strip().upper(), "postal_code": postal_code.strip(), "address_type": address_type}
    errors: dict[str, str] = {}
    if not values["street"] or len(values["street"]) > 160: errors["street"] = "Enter a street address up to 160 characters."
    if not values["city"] or len(values["city"]) > 100: errors["city"] = "Enter a city up to 100 characters."
    if not re.fullmatch(r"[A-Z]{2}", values["state"]): errors["state"] = "Use a two-letter state abbreviation."
    if not POSTAL_RE.fullmatch(values["postal_code"]): errors["postal_code"] = "Use a five-digit ZIP code or ZIP+4."
    if address_type not in {"home", "work", "other"}: errors["address_type"] = "Choose a listed address type."
    return values, errors


def phone_values(phone_number: str, phone_type: str) -> tuple[dict[str, str], dict[str, str]]:
    values = {"phone_number": phone_number.strip(), "phone_type": phone_type}
    errors: dict[str, str] = {}
    if not PHONE_RE.fullmatch(values["phone_number"]): errors["phone_number"] = "Use 7–30 digits and ordinary phone punctuation."
    if phone_type not in {"mobile", "home", "work", "other"}: errors["phone_type"] = "Choose a listed phone type."
    return values, errors
