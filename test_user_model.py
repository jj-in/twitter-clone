"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

app_ctx = app.app_context()
app_ctx.push()

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(f"<User #{u.id}: testuser, test@test.com>", User.__repr__(u))

    def test_follows(self):

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        ) 

        u2 = User(
            email="2@two.com",
            username="two",
            password="HASHED_PASSWORD"
        )    

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        f = Follows(
            user_being_followed_id = u1.id,
            user_following_id = u2.id
        )

        db.session.add(f)
        db.session.commit()

        self.assertTrue(User.is_following(u2, u1))
        self.assertFalse(User.is_following(u1, u2))
        self.assertTrue(User.is_followed_by(u1, u2))
        self.assertFalse(User.is_followed_by(u2, u1))


    def test_user_create(self):

        u1 = User.signup(
        't1',
        't1@test.com',
        'danger',
        'img'
        )

        self.assertEqual('t1', u1.username)

    # def test_dupe_user(self):
    #     """cant figure out which error to raise"""
    #     u1 = User.signup(
    #     't1',
    #     't1@test.com',
    #     'danger',
    #     'img'
    #     )
        
    #     u2 = User.signup(
    #     't1',
    #     't2@test.com',
    #     'danger',
    #     'img'      
    #     )

    def test_bad_info(self):
        with self.assertRaises(ValueError):
            u1 = User.signup(
                't1',
                't1@test.com',
                '',
                'img'
                )

    def test_auth(self):
        with self.assertRaises(AssertionError):
            newUser = User.signup(
            'newguy',
            'new@test.com',
            'danger',
            'img'
            )

            db.session.commit()

            auth = User.authenticate('newguy', 'danger')
            self.assertFalse(auth)

    def fail_auth(self):
        newUser = User.signup(
        'newguy',
        'new@test.com',
        'danger',
        'img'
        )

        db.session.commit()

        auth = User.authenticate('wrong', 'danger')
        self.assertFalse(auth)
        pw = User.authenticate('newguy', 'wrong')
        self.assertFalse(pw)

