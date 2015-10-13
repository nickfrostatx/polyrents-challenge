from mission.app import app as mission_app
import pytest


@pytest.fixture
def app():
    """Creates an HTTP test client for the app"""
    return mission_app.test_client()
