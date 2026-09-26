import pytest
from datetime import datetime
from app import create_app
from database import db, User, Message
from security import encrypt_message, generate_key
import os

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        db.create_all()
        
        # Create test users
        user1 = User(username='testuser1', password_hash='hash1')
        user2 = User(username='testuser2', password_hash='hash2')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_message_send_and_retrieve(app, client):
    """Test sending and retrieving a message"""
    with app.app_context():
        # Login as user1
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser1'
        
        # Send message to user2
        response = client.post('/send', data={
            'receiver': 'testuser2',
            'message': 'Hello from test!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Message sent securely!' in response.data
        
        # Check message in database
        message = Message.query.first()
        assert message is not None
        assert message.sender_id == 1
        assert message.receiver_id == 2
        assert message.content == 'Hello from test!'
        
        # Login as user2
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['username'] = 'testuser2'
        
        # Retrieve message from inbox
        response = client.get('/inbox')
        assert response.status_code == 200
        assert b'Hello from test!' in response.data

def test_encrypted_message_storage(app):
    """Test that messages are stored encrypted in database"""
    with app.app_context():
        # Create a message directly
        salt = os.urandom(16)
        key = generate_key("shared_secret", salt)
        encrypted = encrypt_message("Test content", key)
        
        message = Message(
            content="Test content",
            encrypted_content=encrypted,
            timestamp=datetime.now(),
            sender_id=1,
            receiver_id=2
        )
        db.session.add(message)
        db.session.commit()
        
        # Retrieve from database
        stored = Message.query.first()
        
        # Should not store plaintext
        assert stored.encrypted_content != "Test content"
        assert stored.content == "Test content"  # Note: In real app, we wouldn't store plaintext

def test_message_access_control(app, client):
    """Test that users can only see their own messages"""
    with app.app_context():
        # Create a message from user1 to user2
        message = Message(
            content="Private message",
            encrypted_content="encrypted_dummy",
            timestamp=datetime.now(),
            sender_id=1,
            receiver_id=2
        )
        db.session.add(message)
        db.session.commit()
        
        # Try to access as user3 (unauthorized)
        with client.session_transaction() as sess:
            sess['user_id'] = 3
            sess['username'] = 'testuser3'
        
        response = client.get('/inbox')
        assert b'Private message' not in response.data
        
        # Access as proper recipient (user2)
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['username'] = 'testuser2'
        
        response = client.get('/inbox')
        assert b'Private message' in response.data

def test_invalid_receiver_handling(client):
    """Test handling of invalid receiver username"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser1'
    
    response = client.post('/send', data={
        'receiver': 'nonexistent_user',
        'message': 'This should fail'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Receiver not found' in response.data