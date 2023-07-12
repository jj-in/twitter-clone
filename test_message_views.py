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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res        

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_get_message(self):
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello test world"})
            msg = Message.query.one()
            resp = c.get(f"messages/{msg.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'<p class="single-message">', resp.data)
            self.assertIn(b'Hello test world', resp.data)
            self.assertIn(b'@testuser', resp.data)

    def test_delete_message(self):
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Delete me plz"})
            msg = Message.query.one()
            del_resp = c.post(f"messages/{msg.id}/delete")
            self.assertEqual(del_resp.status_code, 302)
            get_resp = c.get(f"messages/{msg.id}")
            self.assertEqual(get_resp.status_code, 500)

    def test_loggedout_delete(self):
        
        with self.client as c:

            resp1 = c.get("/")
            self.assertIn(b'Sign up now', resp1.data)
            resp2 = c.post("/messages/new", data={"text": "Bad post"})
            self.assertEqual(resp2.status_code, 302)

    
