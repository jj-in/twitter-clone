"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

app_ctx = app.app_context()
app_ctx.push()

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 10000
        self.testuser.id = self.testuser_id

        
        self.u2 = User.signup(username="u2",
                                    email="u2@test.com",
                                    password="testuser",
                                    image_url=None)
        self.u2_id = 9999
        self.u2.id = self.u2_id


        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    
    def test_list_users(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)

            self.assertIn(b'<p class="card-bio">', resp.data)
            self.assertIn(b'@testuser', resp.data)
            self.assertIn(b'@u2', resp.data)

    def test_user_pf(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'fa fa-search', resp.data)
            self.assertIn(b'@testuser', resp.data)



    def test_edit_pf(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp1 = c.get(f"/users/profile")

            self.assertEqual(resp1.status_code, 200)
            self.assertIn(b'@testuser', resp1.data)
            self.assertIn(b'Edit Your Profile', resp1.data)



