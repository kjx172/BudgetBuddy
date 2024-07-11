import pytest
from app import home

def client():
    with home.test_client as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main()