import unittest
from unittest.mock import MagicMock

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from database.models import Contact, User
from schemas import ContactBase, UserModel
from repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirm_email,
    update_avatar
)


class TestRepositoryUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email_found(self):
        user = User()
        self.session.query().filter(User.email == "test@test.com").first.return_value = user
        result = await get_user_by_email(email="test@test.com", db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter(User.email == "test@test.com").first.return_value = None
        result = await get_user_by_email(email="test@test.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        user = UserModel(
            username="test name",
            email="test@test.com",
            password="testpass"
        )
        self.session.query().filter().all.return_value = user
        result = await create_user(body=user, db=self.session)
        self.assertEqual(result.username, user.username)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.password, user.password)
        self.assertTrue(hasattr(result, "id"))


if __name__ == "__main__":
    unittest.main()