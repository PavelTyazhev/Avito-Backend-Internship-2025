import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
import json

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def get_token(username: str, password: str) -> str:
    response = client.post("/api/auth", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["token"]

def test_buy_merch():
    token = get_token("user1", "password")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/buy/t-shirt", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "purchased" in data["message"]
    
    response = client.get("/api/info", headers=headers)
    info = response.json()
    assert info["coins"] == 920
    assert any(item["type"] == "t-shirt" and item["quantity"] == 1 for item in info["inventory"])

def test_send_coin():
    token_alina = get_token("alina", "password")
    token_pavel = get_token("pavel", "password")
    headers_alina = {"Authorization": f"Bearer {token_alina}"}
    headers_pavel = {"Authorization": f"Bearer {token_pavel}"}
    
    response = client.post("/api/sendCoin", json={"toUser": "pavel", "amount": 200}, headers=headers_alina)
    assert response.status_code == 200
    
    info_alina = client.get("/api/info", headers=headers_alina).json()
    info_pavel = client.get("/api/info", headers=headers_pavel).json()
    assert info_alina["coins"] == 800
    assert info_pavel["coins"] == 1200
    
    assert any(tx["toUser"] == "pavel" and tx["amount"] == 200 for tx in info_alina["coinHistory"]["sent"])
    assert any(tx["fromUser"] == "alina" and tx["amount"] == 200 for tx in info_pavel["coinHistory"]["received"])