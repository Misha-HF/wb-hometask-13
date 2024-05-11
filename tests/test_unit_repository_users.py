import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar
from src.schemas import UserModel
from src.database.models import User


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session: Session = MagicMock(spec=Session)
        self.email = "test@mail.com"
        self.user = User(
            id=1, username='username', email=self.email,
            password='password', avatar='avatar.jpg'
        )

    async def test_get_user_by_email(self):
        self.session.query().filter().first.return_value = self.user
        user = await get_user_by_email(email=self.email, db=self.session)
        self.assertEqual(user, self.user)

    async def test_create_user(self):
        body = UserModel(
            username='username', email=self.email, password='password'
        )
        new_user = await create_user(body=body, db=self.session)
        self.assertEqual(new_user.username, 'username')

    async def test_update_token(self):
        res = await update_token(
            user=self.user, token='token', db=self.session
        )
        self.assertIsNone(res)

    async def test_cofirmed_email(self):
        res = await confirmed_email(
            email=self.email, db=self.session
        )
        self.assertIsNone(res)

    
    async def test_update_avatar(self):
        res = await update_avatar(
            email=self.email, url='some_url', db=self.session
        )
        user_from_email = await get_user_by_email(self.email, self.session)
        self.assertEqual(res, user_from_email)

if __name__ == '__main__':
    unittest.main()