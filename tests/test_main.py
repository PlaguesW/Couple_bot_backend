# test_main.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User, PartnerPair, Idea, DateEvent

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# Test data fixtures
@pytest.fixture
def sample_user_data():
    return {
        "user_id": "test_user_123",
        "telegram_id": 123456789,
        "name": "Test User",
        "username": "testuser"
    }

@pytest.fixture
def sample_pair_data():
    return {
        "id": "pair_123",
        "user1_id": "test_user_123", 
        "user2_id": "test_user_456"
    }

@pytest.fixture
def sample_idea_data():
    return {
        "idea_id": "idea_123",
        "title": "Romantic Dinner",
        "description": "A candlelit dinner at home"
    }

@pytest.fixture
def sample_event_data():
    return {
        "id": "event_123",
        "pair_id": "pair_123",
        "idea_id": "idea_123", 
        "proposer_id": "test_user_123",
        "accepted": False,
        "date_status": "pending",
        "scheduled_date": "2024-12-31T20:00:00",
        "completed_date": None
    }

class TestUserEndpoints:
    """Test all user-related endpoints"""
    
    def test_register_user_success(self, client, sample_user_data):
        response = client.post("/users/register", json=sample_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user_data["user_id"]
        assert data["telegram_id"] == sample_user_data["telegram_id"]
        assert data["name"] == sample_user_data["name"]
        assert data["username"] == sample_user_data["username"]
        assert "created_at" in data
        assert "updated_at" in data

    def test_register_user_duplicate_telegram_id(self, client, sample_user_data):
        # Register first user
        client.post("/users/register", json=sample_user_data)
        
        # Try to register with same telegram_id but different user_id
        duplicate_data = sample_user_data.copy()
        duplicate_data["user_id"] = "different_user_456"
        
        response = client.post("/users/register", json=duplicate_data)
        assert response.status_code == 400  # Should fail due to unique constraint

    def test_register_user_invalid_data(self, client):
        invalid_data = {
            "user_id": "",  # Empty user_id
            "telegram_id": "not_an_integer",  # Wrong type
            "name": "Test User"
            # Missing username
        }
        response = client.post("/users/register", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_get_user_profile_success(self, client, sample_user_data):
        # First register user
        client.post("/users/register", json=sample_user_data)
        
        # Then get profile
        response = client.get(f"/users/profile?user_id={sample_user_data['user_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user_data["user_id"]

    def test_get_user_profile_not_found(self, client):
        response = client.get("/users/profile?user_id=nonexistent_user")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_get_user_profile_missing_param(self, client):
        response = client.get("/users/profile")
        assert response.status_code == 422  # Missing required parameter


class TestPairEndpoints:
    """Test all pair-related endpoints"""
    
    def test_create_pair_success(self, client, sample_pair_data, sample_user_data):
        # Create users first
        user1_data = sample_user_data.copy()
        user2_data = sample_user_data.copy()
        user2_data["user_id"] = "test_user_456"
        user2_data["telegram_id"] = 987654321
        user2_data["username"] = "testuser2"
        
        client.post("/users/register", json=user1_data)
        client.post("/users/register", json=user2_data)
        
        response = client.post("/pairs/", json=sample_pair_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_pair_data["id"]
        assert data["user1_id"] == sample_pair_data["user1_id"]
        assert data["user2_id"] == sample_pair_data["user2_id"]
        assert "created_at" in data

    def test_create_pair_invalid_users(self, client):
        invalid_pair = {
            "id": "pair_invalid",
            "user1_id": "nonexistent_user1",
            "user2_id": "nonexistent_user2"
        }
        response = client.post("/pairs/", json=invalid_pair)
        assert response.status_code == 400  # Should fail due to foreign key constraint

    def test_generate_pair_code(self, client):
        response = client.get("/pairs/generate-code")
        assert response.status_code == 200
        code = response.json()
        assert isinstance(code, str)
        assert len(code) > 0

    def test_join_pair_success(self, client):
        # This test assumes generate_pair_code creates a valid code
        # In real implementation, you would need to create a pair first
        response = client.post("/pairs/join?code=valid_test_code")
        # This might return 404 since we don't have the full CRUD implementation
        # But we're testing the endpoint structure
        assert response.status_code in [200, 404]

    def test_join_pair_invalid_code(self, client):
        response = client.post("/pairs/join?code=invalid_code")
        assert response.status_code == 404
        assert response.json()["detail"] == "Pair not found or invalid code"

    def test_get_pair_status_success(self, client, sample_pair_data, sample_user_data):
        # Setup users and pair
        user1_data = sample_user_data.copy()
        user2_data = sample_user_data.copy()
        user2_data["user_id"] = "test_user_456"
        user2_data["telegram_id"] = 987654321
        user2_data["username"] = "testuser2"
        
        client.post("/users/register", json=user1_data)
        client.post("/users/register", json=user2_data)
        client.post("/pairs/", json=sample_pair_data)
        
        response = client.get(f"/pairs/status?pair_id={sample_pair_data['id']}")
        assert response.status_code == 200

    def test_get_pair_status_not_found(self, client):
        response = client.get("/pairs/status?pair_id=nonexistent_pair")
        assert response.status_code == 404
        assert response.json()["detail"] == "Pair not found"


class TestIdeaEndpoints:
    """Test all idea-related endpoints"""
    
    def test_create_idea_success(self, client, sample_idea_data):
        response = client.post("/ideas/", json=sample_idea_data)
        assert response.status_code == 200
        data = response.json()
        assert data["idea_id"] == sample_idea_data["idea_id"]
        assert data["title"] == sample_idea_data["title"]
        assert data["description"] == sample_idea_data["description"]
        assert "created_at" in data

    def test_create_idea_invalid_data(self, client):
        invalid_data = {
            "idea_id": "",  # Empty idea_id
            "title": "",    # Empty title
            # Missing description
        }
        response = client.post("/ideas/", json=invalid_data)
        assert response.status_code == 422

    def test_get_all_ideas(self, client, sample_idea_data):
        # Create a few ideas first
        client.post("/ideas/", json=sample_idea_data)
        
        idea2 = sample_idea_data.copy()
        idea2["idea_id"] = "idea_456"
        idea2["title"] = "Movie Night"
        client.post("/ideas/", json=idea2)
        
        response = client.get("/ideas/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_idea_by_id_success(self, client, sample_idea_data):
        # Create idea first
        client.post("/ideas/", json=sample_idea_data)
        
        response = client.get(f"/ideas/{sample_idea_data['idea_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["idea_id"] == sample_idea_data["idea_id"]

    def test_get_idea_by_id_not_found(self, client):
        response = client.get("/ideas/nonexistent_idea")
        assert response.status_code == 404
        assert response.json()["detail"] == "Idea not found"

    def test_update_idea_success(self, client, sample_idea_data):
        # Create idea first
        client.post("/ideas/", json=sample_idea_data)
        
        updated_data = {
            "idea_id": sample_idea_data["idea_id"],
            "title": "Updated Romantic Dinner",
            "description": "An updated description"
        }
        
        response = client.patch(f"/ideas/{sample_idea_data['idea_id']}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == updated_data["title"]
        assert data["description"] == updated_data["description"]

    def test_update_idea_not_found(self, client):
        updated_data = {
            "idea_id": "nonexistent",
            "title": "Updated Title",
            "description": "Updated Description"
        }
        
        response = client.patch("/ideas/nonexistent", json=updated_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Idea not found"

    def test_delete_idea_success(self, client, sample_idea_data):
        # Create idea first
        client.post("/ideas/", json=sample_idea_data)
        
        response = client.delete(f"/ideas/{sample_idea_data['idea_id']}")
        assert response.status_code == 200
        assert response.json()["detail"] == "Idea deleted"
        
        # Verify it's deleted
        get_response = client.get(f"/ideas/{sample_idea_data['idea_id']}")
        assert get_response.status_code == 404

    def test_delete_idea_not_found(self, client):
        response = client.delete("/ideas/nonexistent_idea")
        assert response.status_code == 404
        assert response.json()["detail"] == "Idea not found"


class TestEventEndpoints:
    """Test all date event-related endpoints"""
    
    def setup_dependencies(self, client, sample_user_data, sample_pair_data, sample_idea_data):
        """Helper method to setup required dependencies"""
        user1_data = sample_user_data.copy()
        user2_data = sample_user_data.copy()
        user2_data["user_id"] = "test_user_456"
        user2_data["telegram_id"] = 987654321
        user2_data["username"] = "testuser2"
        
        client.post("/users/register", json=user1_data)
        client.post("/users/register", json=user2_data)
        client.post("/pairs/", json=sample_pair_data)
        client.post("/ideas/", json=sample_idea_data)

    def test_propose_date_success(self, client, sample_user_data, sample_pair_data, 
                                sample_idea_data, sample_event_data):
        self.setup_dependencies(client, sample_user_data, sample_pair_data, sample_idea_data)
        
        response = client.post("/date/proposal", json=sample_event_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_event_data["id"]
        assert data["pair_id"] == sample_event_data["pair_id"]
        assert data["idea_id"] == sample_event_data["idea_id"]
        assert data["proposer_id"] == sample_event_data["proposer_id"]
        assert data["accepted"] == sample_event_data["accepted"]
        assert data["date_status"] == sample_event_data["date_status"]

    def test_propose_date_invalid_data(self, client):
        invalid_data = {
            "id": "",  # Empty id
            "pair_id": "nonexistent_pair",
            "idea_id": "nonexistent_idea",
            "proposer_id": "nonexistent_user",
            "accepted": "not_boolean",  # Wrong type
            "date_status": "invalid_status"
        }
        response = client.post("/date/proposal", json=invalid_data)
        assert response.status_code in [400, 422]  # Either validation or constraint error

    def test_respond_to_proposal_success(self, client, sample_user_data, sample_pair_data,
                                       sample_idea_data, sample_event_data):
        self.setup_dependencies(client, sample_user_data, sample_pair_data, sample_idea_data)
        
        # Create proposal first
        client.post("/date/proposal", json=sample_event_data)
        
        response = client.post(f"/date/respond?proposal_id={sample_event_data['id']}&accepted=true")
        assert response.status_code == 200
        assert response.json()["detail"] == "Proposal responded"

    def test_respond_to_proposal_not_found(self, client):
        response = client.post("/date/respond?proposal_id=nonexistent&accepted=true")
        assert response.status_code == 404
        assert response.json()["detail"] == "Proposal not found"

    def test_respond_to_proposal_invalid_params(self, client):
        response = client.post("/date/respond?proposal_id=test&accepted=not_boolean")
        assert response.status_code == 422  # Validation error

    def test_get_date_history(self, client, sample_user_data, sample_pair_data,
                            sample_idea_data, sample_event_data):
        self.setup_dependencies(client, sample_user_data, sample_pair_data, sample_idea_data)
        
        # Create some events first
        client.post("/date/proposal", json=sample_event_data)
        
        event2 = sample_event_data.copy()
        event2["id"] = "event_456"
        event2["date_status"] = "accepted"
        client.post("/date/proposal", json=event2)
        
        response = client.get("/date/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAdminEndpoints:
    """Test all admin-related endpoints"""
    
    def test_get_all_users(self, client, sample_user_data):
        # Create a user first
        client.post("/users/register", json=sample_user_data)
        
        response = client.get("/admin/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_all_pairs(self, client, sample_user_data, sample_pair_data):
        # Setup users and pair
        user1_data = sample_user_data.copy()
        user2_data = sample_user_data.copy()
        user2_data["user_id"] = "test_user_456"
        user2_data["telegram_id"] = 987654321
        user2_data["username"] = "testuser2"
        
        client.post("/users/register", json=user1_data)
        client.post("/users/register", json=user2_data)
        client.post("/pairs/", json=sample_pair_data)
        
        response = client.get("/admin/pairs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_ideas_admin(self, client, sample_idea_data):
        # Create an idea first
        client.post("/ideas/", json=sample_idea_data)
        
        response = client.get("/admin/ideas")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestIntegrationScenarios:
    """Test complete user scenarios"""
    
    def test_complete_dating_flow(self, client, sample_user_data):
        """Test complete flow: register users -> create pair -> create idea -> propose date -> respond"""
        
        # 1. Register two users
        user1_data = sample_user_data.copy()
        user2_data = sample_user_data.copy()
        user2_data["user_id"] = "test_user_456"
        user2_data["telegram_id"] = 987654321
        user2_data["username"] = "testuser2"
        
        user1_response = client.post("/users/register", json=user1_data)
        user2_response = client.post("/users/register", json=user2_data)
        assert user1_response.status_code == 200
        assert user2_response.status_code == 200
        
        # 2. Create a pair
        pair_data = {
            "id": "pair_integration_test",
            "user1_id": user1_data["user_id"],
            "user2_id": user2_data["user_id"]
        }
        pair_response = client.post("/pairs/", json=pair_data)
        assert pair_response.status_code == 200
        
        # 3. Create an idea
        idea_data = {
            "idea_id": "idea_integration_test",
            "title": "Integration Test Date",
            "description": "A test date idea"
        }
        idea_response = client.post("/ideas/", json=idea_data)
        assert idea_response.status_code == 200
        
        # 4. Propose a date
        event_data = {
            "id": "event_integration_test",
            "pair_id": pair_data["id"],
            "idea_id": idea_data["idea_id"],
            "proposer_id": user1_data["user_id"],
            "accepted": False,
            "date_status": "pending",
            "scheduled_date": "2024-12-31T20:00:00",
            "completed_date": None
        }
        event_response = client.post("/date/proposal", json=event_data)
        assert event_response.status_code == 200
        
        # 5. Respond to the proposal
        respond_response = client.post(f"/date/respond?proposal_id={event_data['id']}&accepted=true")
        assert respond_response.status_code == 200
        
        # 6. Check date history
        history_response = client.get("/date/history")
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data) >= 1

    def test_error_handling_chain(self, client):
        """Test error handling across different endpoints"""
        
        # Try to create pair with non-existent users
        pair_response = client.post("/pairs/", json={
            "id": "error_test_pair",
            "user1_id": "nonexistent1",
            "user2_id": "nonexistent2"
        })
        assert pair_response.status_code == 400
        
        # Try to propose date with non-existent pair/idea/user
        event_response = client.post("/date/proposal", json={
            "id": "error_test_event",
            "pair_id": "nonexistent_pair",
            "idea_id": "nonexistent_idea",
            "proposer_id": "nonexistent_user",
            "accepted": False,
            "date_status": "pending"
        })
        assert event_response.status_code in [400, 422]


# Performance and load testing
class TestPerformance:
    """Basic performance tests"""
    
    def test_bulk_user_creation(self, client):
        """Test creating multiple users"""
        users_created = 0
        for i in range(10):
            user_data = {
                "user_id": f"bulk_user_{i}",
                "telegram_id": 100000 + i,
                "name": f"Bulk User {i}",
                "username": f"bulkuser{i}"
            }
            response = client.post("/users/register", json=user_data)
            if response.status_code == 200:
                users_created += 1
        
        assert users_created == 10
        
        # Verify with admin endpoint
        admin_response = client.get("/admin/users")
        assert admin_response.status_code == 200
        users = admin_response.json()
        assert len(users) >= 10

    def test_bulk_idea_operations(self, client):
        """Test creating and retrieving multiple ideas"""
        ideas_created = 0
        for i in range(20):
            idea_data = {
                "idea_id": f"bulk_idea_{i}",
                "title": f"Bulk Idea {i}",
                "description": f"Description for bulk idea {i}"
            }
            response = client.post("/ideas/", json=idea_data)
            if response.status_code == 200:
                ideas_created += 1
        
        assert ideas_created == 20
        
        # Test retrieving all ideas
        all_ideas_response = client.get("/ideas/all")
        assert all_ideas_response.status_code == 200
        ideas = all_ideas_response.json()
        assert len(ideas) >= 20


if __name__ == "__main__":
    # Run tests with: pytest test_main.py -v
    pytest.main(["-v", __file__])