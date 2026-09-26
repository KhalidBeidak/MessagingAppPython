import pytest
from security import hash_password, verify_password, generate_key, encrypt_message, decrypt_message
import base64

def test_password_hashing_and_verification():
    """Test that password hashing and verification works correctly"""
    password = "SecurePass123!"
    hashed = hash_password(password)
    
    # Should verify correct password
    assert verify_password(password, hashed) is True
    
    # Should reject incorrect password
    assert verify_password("WrongPassword", hashed) is False
    
    # Different salts should produce different hashes
    hashed2 = hash_password(password)
    assert hashed != hashed2

def test_encryption_decryption():
    """Test that encryption and decryption works correctly"""
    message = "This is a secret message!"
    password = "encryption_password"
    salt = b'salt_1234567890'  # 16 bytes
    
    # Generate key
    key = generate_key(password, salt)
    
    # Encrypt the message
    encrypted = encrypt_message(message, key)
    
    # Should not be plaintext
    assert encrypted != message
    assert isinstance(encrypted, str)
    
    # Decrypt the message
    decrypted = decrypt_message(encrypted, key)
    
    # Should match original
    assert decrypted == message

def test_encryption_with_different_keys():
    """Test that decryption fails with incorrect key"""
    message = "Confidential data"
    salt = b'fixed_salt_value_'
    
    # Create two different keys
    key1 = generate_key("password1", salt)
    key2 = generate_key("password2", salt)
    
    # Encrypt with key1
    encrypted = encrypt_message(message, key1)
    
    # Try to decrypt with key2 - should fail
    with pytest.raises(Exception):
        decrypt_message(encrypted, key2)

def test_key_generation_consistency():
    """Test that same password+salt produces same key"""
    password = "consistent_key"
    salt = b'fixed_salt_value_'
    
    key1 = generate_key(password, salt)
    key2 = generate_key(password, salt)
    
    assert key1 == key2