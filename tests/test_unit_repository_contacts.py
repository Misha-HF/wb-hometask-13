
import unittest
from unittest.mock import MagicMock
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.repository.contacts import get_contacts, get_contact, get_contact_by_phone, get_contact_by_email, create_contact,update_contact, delete_contact, get_contacts_by_birthday, search_contacts
from src.schemas import ContactBase, ContactUpdate
from src.database.models import Contact, User


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

        self.mock_contacts = [
            Contact(
                id=1, first_name="Bob", last_name="Black", email="bob@example.com",
                phone_number="12345678910", birthday=date(year=1999, month=5, day=12), user_id=1
            )
        ]

    async def test_get_contacts(self):
        contacts_item = [Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts_item
        contacts = await get_contacts(
            db=self.session, user=self.user, skip=0, limit=10
        )
        self.assertEqual(contacts, contacts_item)
    

    async def test_get_contact(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        contact_res = await get_contact(
            db=self.session, user=self.user, contact_id=1)
        self.assertEqual(contact_res, contact)


    async def test_get_contact_None(self):
        self.session.query().filter().first.return_value = None
        contact = await get_contact(
            db=self.session, user=self.user, contact_id=1)
        self.assertIsNone(contact)


    async def test_get_contacts_by_phone(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        contacts = await get_contact_by_phone(
            db=self.session, user=self.user, phone_number = "12345678910")
        self.assertEqual(contact, contacts)

    async def test_get_contacts_by_phone_None(self):
        self.session.query().filter().first.return_value = None
        contacts = await get_contact_by_phone(
            db=self.session, user=self.user, phone_number = "12345678910")
        self.assertEqual(contacts, None)

    async def test_get_contact_by_email(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        contacts = await get_contact_by_email(
            email="bob@example.com", user=self.user, db=self.session
        )
        self.assertEqual(contact, contacts)

    async def test_get_contact_by_email_None(self):
        self.session.query().filter().first.return_value = None
        contacts = await get_contact_by_email(
            email="bob@example.com", user=self.user, db=self.session
        )
        self.assertIsNone(contacts)

    async def test_create_contact(self):
        contact_data = ContactBase(
            first_name="Bob", last_name="Black", email="bob@example.com",
            phone_number="12345678910", birthday=date(year=1999, month=5, day=12)
        )
        new_contact = await create_contact(
            contact=contact_data, user=self.user, db=self.session
        )
        self.assertEqual(new_contact.first_name, contact_data.first_name)
        self.assertEqual(new_contact.email, contact_data.email)
        self.assertEqual(new_contact.phone_number, contact_data.phone_number)
        self.assertTrue(hasattr(new_contact, "id"))

    async def test_update_contact(self):
        contact_data = ContactUpdate(
            completed=True, first_name="Bob1", last_name="Black1", email="bob1@example.com",
            phone_number="12345678910", birthday=date(year=1999, month=5, day=12)
        )
        updated_contact = await update_contact(
            contact=contact_data, db_contact=self.mock_contacts[0], user=self.user, db=self.session
        )
        self.assertEqual(updated_contact.first_name, "Bob1")
        self.assertEqual(updated_contact.last_name, "Black1")
        self.assertEqual(updated_contact.email, "bob1@example.com")


    async def test_search_contacts(self):
        contacts_item = Contact()
        self.session.query().filter().all.return_value = contacts_item
        contacts = await search_contacts(
            user=self.user, db=self.session, first_name="Bob", last_name="Black", email="bob@example.com"
        )
        self.assertEqual(contacts, contacts_item)

    async def test_search_contacts_None(self):
        self.session.query().filter().all.return_value = None
        contacts = await search_contacts(
            user=self.user, db=self.session, first_name="Bob", last_name="Black", email="bob@example.com"
        )
        self.assertIsNone(contacts)

    async def test_delete_contact(self):
        get_contact.return_value = Contact()
        res = await delete_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertIsNone(res)


    async def test_get_contacts_by_birthday(self):
        contacts_item = [Contact(), Contact(), Contact()]
        self.session.query().where().all.return_value = contacts_item
        today = date.today()
        week_later = today + timedelta(days=7)
        birthdays =  await get_contacts_by_birthday(user=self.user, db=self.session, start_date=today, end_date=week_later)
        self.assertEqual(contacts_item, birthdays)

if __name__ == '__main__':
    unittest.main()
