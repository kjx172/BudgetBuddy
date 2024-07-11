import pytest
import app

def client():
    with app.test_client as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main()