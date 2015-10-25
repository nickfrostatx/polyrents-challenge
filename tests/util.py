from mission.app import app as mission_app
import fakeredis
import pytest


@pytest.fixture
def app():
    """Create an HTTP test client for the app."""
    mission_app.config['TESTING'] = True
    mission_app.redis = fakeredis.FakeStrictRedis()
    return mission_app.test_client()
