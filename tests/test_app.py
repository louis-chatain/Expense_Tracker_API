import pytest
import json
from backend.config import app, db, uri # Import necessary components from your application
from backend.models import User, Expense
from werkzeug.security import generate_password_hash, check_password_hash
# --- Pytest Fixtures ---

@pytest.fixture(scope="session")
def flask_app():
    """Fixture for the main Flask application instance."""
    app.config['TESTING'] = True
    # Ensure the PostgreSQL config is loaded
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    # Replace with your actual connection string
    yield app

@pytest.fixture(scope="session")
def client(flask_app):
    """Fixture for a test client."""
    return flask_app.test_client()

# --- Corrected Fixture in test_app.py ---

@pytest.fixture(scope="function", autouse=True)
def init_database(flask_app):
    """
    Fixture to initialize the database and manage transactions for each test.
    Uses nested transactions for quick cleanup.
    """
    with flask_app.app_context():
        # 1. Create all tables if they don't exist
        db.create_all()

        # 2. Start a connection and transaction
        # Use db.engine.begin() for simplified transaction management
        connection = db.engine.connect()
        transaction = connection.begin()

        # 3. Create a new SQLAlchemy Session bound to the connection
        # This replaces the need for db.create_scoped_session
        session = db.Session(bind=connection)
        
        # NOTE: If you are using Flask-SQLAlchemy 3.x, accessing db.session directly 
        # might be deprecated/removed for custom session management.
        # We'll use the new session explicitly for setup, and let the application 
        # use its standard db.session (which is often a scoped session) during the test run.
        
        # 4. Insert a test user using the explicit session
        test_email = "test@example.com"
        test_password = "password123"
        hashed_password = generate_password_hash(
            test_password, method="pbkdf2:sha1", salt_length=24
        )
        test_user = User(email=test_email, hashed_password=hashed_password)
        session.add(test_user)
        session.commit()
        
        # Store the connection and transaction so they can be accessed 
        # for cleanup after the test runs.
        yield session # Yield the explicit session for the test to use for checks

        # 5. Teardown: Rollback the transaction to revert all changes
        session.close()
        transaction.rollback() # Rollback all test data
        connection.close()
        
        # Re-bind the standard session after cleanup (optional, but safe)
        db.session.remove()

# --- Utility Functions (Ensure they use the session passed from the fixture for DB operations if possible) ---

# --- Utility Functions ---

def register_user(client, email, password):
    """Helper to register a user via the /sign_up endpoint."""
    return client.post(
        "/sign_up",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json"
    )

def login_user(client, email, password):
    """Helper to log in a user via the /login endpoint."""
    return client.post(
        "/login",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json"
    )

# --- Tests for Routes ---

## Test /sign_up
def test_sign_up_success(client, init_database, flask_app):
    """Test successful user registration."""
    new_email = "newuser@test.com"
    new_password = "securepassword"
    
    response = register_user(client, new_email, new_password)
    
    # Successful sign up returns 200 OK with no content in your code
    assert response.status_code == 200 
    
    # Verify user is in the database using the session from the fixture
    user = init_database.query(User).filter_by(email=new_email).first()
    assert user is not None
    assert check_password_hash(user.hashed_password, new_password)

def test_sign_up_email_in_use(client, init_database):
    """Test user registration with an already existing email."""
    existing_email = "test@example.com" # Exists from init_database fixture
    
    response = register_user(client, existing_email, "anotherpass")
    
    assert response.status_code == 200 
    assert json.loads(response.data) == {"message": "This email is already in use."}

# ---

## Test /login

# NOTE: The /login logic in app.py is incorrect and insecure.
# The tests below reflect the flawed behavior of your original code.
# You MUST fix the /login function in app.py for correct security.
# Correct login logic: user = User.query.filter_by(email=email).first(); if user and check_password_hash(user.hashed_password, password): login_user(user)

def test_login_success(client, init_database):
    """Test successful user login (based on the flawed logic)."""
    response = login_user(client, "test@example.com", "password123")

    # The login function returns nothing on success, resulting in 200 OK
    assert response.status_code == 200
    # A successful login sets a session cookie
    assert 'session' in response.headers.get('Set-Cookie', '') 

def test_login_user_not_found(client, init_database):
    """Test login with an email not in the database."""
    response = login_user(client, "unknown@test.com", "password123")
    
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "the user email is not found in the database"}

def test_login_incorrect_password(client, init_database):
    """Test login with correct email but incorrect password (based on the flawed logic)."""
    response = login_user(client, "test@example.com", "wrong_password")
    
    # Due to the flawed logic, the password check fails and the code falls through
    # to return the "email is not found" message.
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "the user email is not found in the database"}

# ---

## Test /logout and /sign_out

def test_logout_success(client, init_database):
    """Test successful user logout."""
    # 1. Login the user to establish a session
    login_user(client, "test@example.com", "password123")
    
    # 2. Logout the user
    response = client.post("/logout")
    
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "user has been logged out"}
    
def test_sign_out_success(client, init_database):
    """Test successful user account deletion and logout."""
    # 1. Login the user
    login_user(client, "test@example.com", "password123")
    
    # 2. Get user ID before sign_out
    user_to_delete = init_database.query(User).filter_by(email="test@example.com").first()
    user_id = user_to_delete.id
    
    # 3. Sign out/Delete account
    response = client.post("/sign_out")
    
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "this user has been deleted and logged outs"}
    
    # 4. Verify user is deleted from the database
    deleted_user = init_database.query(User).get(user_id)
    assert deleted_user is None

def test_requires_login(client, init_database):
    """Test that protected routes redirect/fail when not logged in."""
    # Test /logout
    response_logout = client.post("/logout")
    assert response_logout.status_code == 401 # Should be 401 Unauthorized by default

    # Test /sign_out
    response_sign_out = client.post("/sign_out")
    assert response_sign_out.status_code == 401