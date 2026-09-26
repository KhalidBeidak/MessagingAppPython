from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, User, Message
from security import hash_password, verify_password, generate_key, encrypt_message, decrypt_message
from datetime import datetime
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secure_messenger.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app()

with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('inbox'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        
        hashed_pw = hash_password(password)
        salt = os.urandom(16)                        # Generate a secure 16-byte salt
        encryption_key = generate_key(password, salt)  # Derive key using password and salt
        
        new_user = User(
            username=username, 
            password_hash=hashed_pw, 
            salt=salt, 
            encryption_key=encryption_key
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and verify_password(password, user.password_hash):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('inbox'))
        
        flash('Invalid username or password.')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    messages = Message.query.filter_by(receiver_id=current_user.id).all()
    
    decrypted_messages = []
    for msg in messages:
        try:
            # security.py expects: decrypt_message(encrypted_message, key)
            decrypted_body = decrypt_message(msg.encrypted_content, current_user.encryption_key)
        except Exception:
            decrypted_body = "[Decryption Failed]"
            
        decrypted_messages.append({
            'sender': User.query.get(msg.sender_id).username,
            'body': decrypted_body,
            'timestamp': msg.timestamp
        })
        
    return render_template('inbox.html', messages=decrypted_messages)

@app.route('/send', methods=['GET', 'POST'])
def send():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        recipient_username = request.form.get('recipient')
        raw_message = request.form.get('message')
        
        recipient = User.query.filter_by(username=recipient_username).first()
        if not recipient:
            flash('Recipient not found.')
            return redirect(url_for('send'))
            
        # security.py expects: encrypt_message(message, key)
        encrypted_body = encrypt_message(raw_message, recipient.encryption_key)
        
        new_msg = Message(
            sender_id=session['user_id'],
            receiver_id=recipient.id,
            encrypted_content=encrypted_body,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_msg)
        db.session.commit()
        
        flash('Message sent securely!')
        return redirect(url_for('inbox'))
        
    users = User.query.filter(User.id != session['user_id']).all()
    return render_template('send.html', users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(ssl_context='adhoc', debug=True)