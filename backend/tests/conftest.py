import pytest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.config import Config

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DEBUG": False
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_client(app):
    # Independent client logged in as demo passenger
    c = app.test_client()
    c.post('/api/auth/login', json={
        "email": "user@railsync.com",
        "password": "User@123"
    })
    return c

@pytest.fixture
def admin_client(app):
    # Independent client logged in as demo administrator
    c = app.test_client()
    c.post('/api/auth/login', json={
        "email": "admin@railsync.com",
        "password": "Admin@123"
    })
    return c
