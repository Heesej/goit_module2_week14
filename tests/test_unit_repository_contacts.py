import unittest
from unittest.mock import MagicMock

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from database.models import Contact, User
from schemas import ContactBase
from repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
    check_contact
)


class TestRepositoryContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact_base = ContactBase(
            first_name="test name",
            last_name="test last name",
            email="test1@example.com",
            phone="123456789",
            date_of_birth="2000-02-27",
            additional_data="test friend"
        )

    async def test_get_contacts_without_filters(self):
        contacts = [Contact(), Contact(), Contact()]
        skip = 0
        limit = 10
        self.session.query(Contact).filter(Contact.user_id == self.user.id). \
            offset(skip).limit(limit).all.return_value = contacts

        result = await get_contacts(first_name=None, last_name=None, email=None, user=self.user,
                                    db=self.session, skip=skip,
                                    limit=limit)

        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        result = await create_contact(body=self.contact_base, user=self.user, db=self.session)
        self.assertEqual(result.first_name, self.contact_base.first_name)
        self.assertEqual(result.last_name, self.contact_base.last_name)
        self.assertEqual(result.email, self.contact_base.email)
        self.assertEqual(result.phone, self.contact_base.phone)
        self.assertEqual(result.date_of_birth, self.contact_base.date_of_birth)
        self.assertEqual(result.additional_data, self.contact_base.additional_data)
        self.assertTrue(hasattr(result, "id"))

    async def test_check_contact_with_email(self):
        contact = self.session.query().filter(
            and_(Contact.user_id == self.user.id, Contact.email == "test1@example.com")).first()
        result = await check_contact(email="test1@example.com", phone=None, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_check_contact_with_phone(self):
        contact = self.session.query().filter(
            and_(Contact.user_id == self.user.id, Contact.phone == "12345678963")).first()
        result = await check_contact(email=None, phone="12345678963", user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_check_contact_with_email_and_phone(self):
        contact = self.session.query().filter(
            and_(Contact.user_id == self.user.id,
                 or_(Contact.email == "test1@example.com", Contact.phone == "12345678963"))).first()
        result = await check_contact(email="test1@example.com", phone="12345678963", user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_found(self):
        self.session.query().filter().first.return_value = self.contact_base
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=self.contact_base, user=self.user, db=self.session)
        self.assertEqual(result, self.contact_base)

    async def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=self.contact_base, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
