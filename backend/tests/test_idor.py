import pytest
from fastapi.testclient import TestClient
from main import app

def test_assessment_report_history_idor(client, db_session):
    # Crie o User 1
    user1_response = client.post("/api/v1/users/", json={"name": "User One", "email": "user1-idor@example.com", "password": "Password123"})
    assert user1_response.status_code == 200
    user1_id = user1_response.json()["id"]

    # Login como User 1
    login1_response = client.post("/api/v1/auth/login", data={"username": "user1-idor@example.com", "password": "Password123"})
    assert login1_response.status_code == 200
    
    # We will use the main client to handle User 1's requests, let's keep it simple
    client1 = TestClient(app)
    client1.cookies.update(login1_response.cookies)

    # Directly create an assessment attempt in the database to avoid Neo4j dependency
    from models.assessment import AssessmentAttempt
    new_attempt = AssessmentAttempt(user_id=user1_id, type="diagnostico", analysis_json={"title": "Test"})
    db_session.add(new_attempt)
    db_session.commit()
    db_session.refresh(new_attempt)
    attempt_id = new_attempt.id

    # Verifica se User 1 consegue acessar seu próprio attempt
    attempt1_response = client1.get(f"/api/v1/assessment-report/history/{attempt_id}")
    assert attempt1_response.status_code == 200

    # Crie o User 2
    user2_response = client.post("/api/v1/users/", json={"name": "User Two", "email": "user2-idor@example.com", "password": "Password123"})
    assert user2_response.status_code == 200

    # Login como User 2
    login2_response = client.post("/api/v1/auth/login", data={"username": "user2-idor@example.com", "password": "Password123"})
    assert login2_response.status_code == 200
    
    client2 = TestClient(app)
    client2.cookies.update(login2_response.cookies)

    # User 2 tenta acessar o attempt do User 1 (Teste IDOR)
    idor_response = client2.get(f"/api/v1/assessment-report/history/{attempt_id}")
    
    # Esperado: 404 (já que na busca é filtrado pelo user_id e não encontrará, retornando 404)
    # ou 403 se fosse explicitamente bloqueado.
    assert idor_response.status_code in [403, 404], f"IDOR Vulnerability detected! Expected 403 or 404, got {idor_response.status_code}"
