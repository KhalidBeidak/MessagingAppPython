# Secure Messaging Web Application

A lightweight, secure web-based messaging platform built with Python and Flask. This application implements robust user authentication and cryptographic message encryption to ensure privacy and data security.

## Features

* Secure User Authentication: Passwords are securely hashed using `bcrypt`.

* End-to-End Cryptography: Employs PBKDF2-HMAC key derivation and Fernet symmetric encryption to protect user messages.

* Messaging & Inbox: Registered users can send encrypted messages to each other and view decrypted messages securely in their personal inbox.

* HTTPS Support: Runs locally with a secure ad-hoc SSL context (`ssl_context='adhoc'`).

* Automated Test Suite: Includes unit tests covering authentication, encryption, and messaging functionalities via `pytest`.

## Tech Stack

* Backend: Python, Flask, Flask-SQLAlchemy

* Security: `bcrypt`, `cryptography` (Fernet / PBKDF2)

* Database: SQLite

* Testing: `pytest`

* Frontend: HTML5, Jinja2 Templates

## Project Structure

`project/`
`│`
`├── app.py              # Main Flask application and routes`
`├── database.py         # SQLAlchemy database models (User, Message)`
`├── security.py         # Hashing, key derivation, and encryption logic`
`├── static/             # Static assets (CSS, etc.)`
`├── templates/          # HTML templates (login, register, inbox, send, base)`
`└── tests/              # Automated unit tests (pytest)`

## Getting Started

### Prerequisites

Python 3.8+ installed on your system.

### Installation & Setup

1. Clone the repository:
   `git clone https://github.com/YourUsername/your-repo-name.git`
   `cd project/MessagingApp`

2. Create and activate a virtual environment:

   * Windows (PowerShell):
     `python -m venv venv`
     `.\venv\Scripts\Activate`

   * macOS / Linux:
     `python3 -m venv venv`
     `source venv/bin/activate`

3. Install dependencies:
   `pip install flask flask-sqlalchemy bcrypt cryptography pytest`

## Running the Application

1. Start the Flask server:
   `python app.py`

2. Open your web browser and navigate to:
   `https://127.0.0.1:5000/register`
   (Note: Because the app uses a self-signed development certificate, your browser may display a security warning. Click Advanced and then Proceed to 127.0.0.1 (unsafe) to access the app).

## (Optional) Remote Testing with Ngrok

If you want to test the application with a peer in another country or on a different network, you can use **ngrok** to expose your local host to a secure public URL.

1. Download and set up **ngrok** from [ngrok.com](https://ngrok.com/) and create a free account.
2. Authenticate your ngrok client using your account authtoken:
   `ngrok config add-authtoken YOUR_AUTH_TOKEN`
3. With your Flask application running locally (`python app.py`), open a second terminal window.
4. Start the ngrok tunnel pointing directly to your local HTTPS server:
   `ngrok http https://localhost:5000`
5. Copy the generated public forwarding URL (e.g., `https://xxxx-xxxx.ngrok-free.dev`) and share it with your peer. They can open the link in their browser, create an account, and test sending encrypted messages cross-region!

## Running Automated Tests

To run the unit test suite and verify system functionality:
`pytest`