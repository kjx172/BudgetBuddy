import pytest
from unittest.mock import patch
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'  # Set SECRET_KEY for testing
    app.config['SERVER_NAME'] = 'localhost'  # Set SERVER_NAME for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})  # Mock the environment variable
@patch('app.OpenAI')  # Mock the OpenAI client
def test_home_page(mock_openai, client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data  # Assuming the login page contains 'Login'

@patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})  # Mock the environment variable
@patch('app.OpenAI')  # Mock the OpenAI client
def test_user_registration(mock_openai, client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword',
        'form_type': 'sign-up'
    })
    assert response.status_code == 302  # Redirect to login page after signup
    user = User.query.filter_by(username='testuser').first()
    assert user is not None

if __name__ == "__main__":
    pytest.main()
