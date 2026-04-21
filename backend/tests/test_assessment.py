from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db
from backend.core.neo4j import get_driver
import pytest

client = TestClient(app)

def test_get_assessment(client):
    response = client.get("/api/v1/assessment")
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) > 0

def test_submit_assessment(client, neo4j_driver):
    # Create a test user
    user_response = client.post("/api/v1/users/", json={"name": "Test User", "email": "test@example.com", "password": "test"})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Create some test concepts in Neo4j
    with neo4j_driver.session() as session:
        session.run("CREATE (c:Concept {name: 'Geografia'})")
        session.run("CREATE (c:Concept {name: 'Matemática'})")

    # Get assessment to have some questions to answer
    assessment_response = client.get("/api/v1/assessment")
    questions = assessment_response.json()["questions"]

    # Find correct and incorrect answers
    correct_answers = []
    incorrect_answers = []
    for q in questions:
        correct_option_id = q.get('correct_option_id')
        if not correct_option_id:
            continue

        correct_option = next((o for o in q['options'] if o['id'] == correct_option_id), None)
        incorrect_option = next((o for o in q['options'] if o['id'] != correct_option_id), None)

        if correct_option:
            correct_answers.append({"question_id": q["id"], "selected_option_id": correct_option["id"]})
        if incorrect_option:
            incorrect_answers.append({"question_id": q["id"], "selected_option_id": incorrect_option["id"]})


    # Submit some answers
    submission_data = {
        "user_id": user_id,
        "answers": [correct_answers[0], incorrect_answers[1]]
    }
    response = client.post("/api/v1/assessment/submit", json=submission_data)
    assert response.status_code == 200

    # (Optional) Verify proficiency in Neo4j
    with neo4j_driver.session() as session:
        result = session.run(
            "MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(c:Concept) RETURN r.score as score, c.name as concept_name",
            user_id=user_id
        )
        proficiencies = {record["concept_name"]: record["score"] for record in result}
        assert "Geografia" in proficiencies
        assert proficiencies["Geografia"] == 1.0
        assert "Matemática" in proficiencies
        assert proficiencies["Matemática"] == 0.0

    # Cleanup
    with neo4j_driver.session() as session:
        session.run("MATCH (u:User {id: $user_id}) DETACH DELETE u", user_id=user_id)
        session.run("MATCH (c:Concept {name: 'Geografia'}) DETACH DELETE c")
        session.run("MATCH (c:Concept {name: 'Matemática'}) DETACH DELETE c")
