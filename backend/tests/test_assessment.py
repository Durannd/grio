from fastapi.testclient import TestClient
from main import app
from core.neo4j import get_driver
import pytest

client = TestClient(app)

def test_submit_assessment(client, neo4j_driver):
    # Create a test user
    user_response = client.post("/api/v1/users/", json={"name": "Test User", "email": "test-assessment@example.com", "password": "test"})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Login to get token (now via cookie)
    login_response = client.post("/api/v1/auth/login", data={"username": "test-assessment@example.com", "password": "test"})
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies

    # Get assessment questions
    assessment_response = client.get("/api/v1/assessment")
    if assessment_response.status_code != 200:
        print(assessment_response.json())
    assert assessment_response.status_code == 200
    questions = assessment_response.json()["questions"]

    # Select an answer for the first question
    first_question = questions[0]
    # In the real API, correct_option_id is not returned. We pick option 1.
    selected_option_id = 1

    # Submit the assessment
    submission_data = {
        "user_id": user_id,
        "answers": [{"question_id": first_question["id"], "selected_option_id": selected_option_id, "time_seconds": 10}]
    }

    response = client.post("/api/v1/assessment/submit", json=submission_data)
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200

    # Verify proficiency in Neo4j
    with neo4j_driver.session() as session:
        result = session.run(
            "MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(target) RETURN r.score as score",
            user_id=user_id
        )
        record = result.single()
        # The score might not be 1.0 if we picked the wrong answer, 
        # but it should exist if the submission was processed.
        assert record is not None
