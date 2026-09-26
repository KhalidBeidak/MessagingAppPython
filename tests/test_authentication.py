import pytest
from app import app as flask_app
from database import db, User

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

def test_user_registration(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 302  # Redirect after registration
    
    user = User.query.filter_by(username='testuser').first()
    assert user is not None

def test_user_login(client):
    # First register a user
    client.post('/register', data={
        'username': 'testuser',
        'password': 'SecurePass123!'
    })
    
    # Then login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 302  # Redirect after login
    assert 'user_id' in client.get('/').request.context['session']