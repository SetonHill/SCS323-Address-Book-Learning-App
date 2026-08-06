from sqlalchemy import select

from .database import SessionLocal
from .models import Address, Contact, PhoneNumber

SEED = [
    ("Avery", "Morgan", "avery.morgan@example.test", [("18 Walnut Street", "Greensburg", "PA", "15601", "home")], [("724-555-0134", "mobile")]),
    ("Jordan", "Lee", "jordan.lee@example.test", [("420 College Avenue", "Pittsburgh", "PA", "15213", "work")], [("412-555-0182", "work"), ("724-555-0109", "mobile")]),
    ("Sam", "Rivera", "sam.rivera@example.test", [], [("814-555-0177", "home")]),
]


def main() -> None:
    with SessionLocal() as session:
        if session.scalar(select(Contact.id).limit(1)):
            print("Seed skipped: contacts already exist.")
            return
        for first, last, email, addresses, phones in SEED:
            contact = Contact(first_name=first, last_name=last, email=email)
            contact.addresses = [Address(street=a[0], city=a[1], state=a[2], postal_code=a[3], address_type=a[4]) for a in addresses]
            contact.phone_numbers = [PhoneNumber(phone_number=p[0], phone_type=p[1]) for p in phones]
            session.add(contact)
        session.commit()
    print("Seeded 3 synthetic contacts.")


if __name__ == "__main__": main()
