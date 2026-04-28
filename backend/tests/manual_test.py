import httpx
import pytest

def test_submit_assessment_manual(client):
    # Dados do usuário e da prova
    email = "manual-test@example.com"
    password = "Password123"
    user_data = {"name": "Manual Test User", "email": email, "password": password}

    # Criar usuário
    user_response = client.post("/api/v1/users/", json=user_data)
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Login (necessário para o cookie de autenticação)
    login_response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert login_response.status_code == 200

    # Obter prova
    assessment_response = client.get("/api/v1/assessment")
    assert assessment_response.status_code == 200
    questions = assessment_response.json()["questions"]

    # Enviar resposta
    submission_data = {
        "user_id": user_id,
        "answers": [{"question_id": questions[0]["id"], "selected_option_id": questions[0]["options"][0]["id"]}]
    }
    submit_response = client.post("/api/v1/assessment/submit", json=submission_data)
    assert submit_response.status_code == 200

    # A verificação no Neo4j teria que ser feita manualmente ou com um script separado
    # Por agora, o teste se concentra em garantir que o endpoint responde corretamente
