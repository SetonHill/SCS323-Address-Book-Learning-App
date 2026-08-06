from app.validation import address_values, contact_values, phone_values


def test_contact_validation_normalizes_email():
    values, errors = contact_values(" Avery ", " Morgan ", "AVERY@EXAMPLE.TEST")
    assert errors == {}
    assert values == {"first_name": "Avery", "last_name": "Morgan", "email": "AVERY@example.test"}


def test_invalid_contact_values_are_safe_and_specific():
    _, errors = contact_values("", "<script>", "not-an-email")
    assert set(errors) == {"first_name", "last_name", "email"}


def test_address_and_phone_constraints():
    _, address_errors = address_values("1 Main St", "Greensburg", "Pennsylvania", "bad", "planet")
    _, phone_errors = phone_values("call me", "pager")
    assert set(address_errors) == {"state", "postal_code", "address_type"}
    assert set(phone_errors) == {"phone_number", "phone_type"}
