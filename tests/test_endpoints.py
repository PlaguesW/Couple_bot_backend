import uuid
from datetime import datetime

def test_user_registration(client):
    response = client.post("/users/register", json={
        "user_id": str(uuid.uuid4()),
        "telegram_id": 123456789,
        "name": "Test User",
        "username": "testuser"
    })
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "created_at" in data

def test_get_user_profile(client):
    user_id = str(uuid.uuid4())
    client.post("/users/register", json={
        "user_id": user_id,
        "telegram_id": 987654321,
        "name": "Another User",
        "username": "anotheruser"
    })
    response = client.get(f"/users/profile?user_id={user_id}")
    assert response.status_code == 200
    assert response.json()["user_id"] == user_id

def test_create_pair(client):
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    pair_id = str(uuid.uuid4())

    client.post("/users/register", json={
        "user_id": user1_id,
        "telegram_id": 1,
        "name": "User1",
        "username": "user1"
    })

    client.post("/users/register", json={
        "user_id": user2_id,
        "telegram_id": 2,
        "name": "User2",
        "username": "user2"
    })

    response = client.post("/pairs/", json={
        "id": pair_id,
        "user1_id": user1_id,
        "user2_id": user2_id
    })
    assert response.status_code == 200
    assert response.json()["id"] == pair_id

def test_create_idea(client):
    idea_id = str(uuid.uuid4())
    response = client.post("/ideas/", json={
        "idea_id": idea_id,
        "title": "Test Idea",
        "description": "Do something fun"
    })
    assert response.status_code == 200
    assert response.json()["idea_id"] == idea_id

def test_get_all_ideas(client):
    response = client.get("/ideas/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_propose_date_event(client):
    # Предположим, пара и идея уже есть
    pair_id = str(uuid.uuid4())
    idea_id = str(uuid.uuid4())
    proposer_id = str(uuid.uuid4())

    # зарегистрируем всё
    client.post("/users/register", json={
        "user_id": proposer_id,
        "telegram_id": 111,
        "name": "Proposer",
        "username": "proposer"
    })

    client.post("/pairs/", json={
        "id": pair_id,
        "user1_id": proposer_id,
        "user2_id": str(uuid.uuid4())
    })

    client.post("/ideas/", json={
        "idea_id": idea_id,
        "title": "Dinner",
        "description": "Romantic dinner"
    })

    response = client.post("/date/proposal", json={
        "id": str(uuid.uuid4()),
        "pair_id": pair_id,
        "idea_id": idea_id,
        "proposer_id": proposer_id,
        "accepted": False,
        "date_status": "pending"
    })
    assert response.status_code == 200
    assert response.json()["date_status"] == "pending"

def test_admin_get_all_users(client):
    response = client.get("/admin/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_get_all_pairs(client):
    response = client.get("/admin/pairs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_get_all_ideas(client):
    response = client.get("/admin/ideas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)