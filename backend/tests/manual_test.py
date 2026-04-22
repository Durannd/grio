import httpx
import pytest

def test_submit_assessment_manual():
    # Dados do usuário e da prova
    user_data = {"name": "Manual Test User", "email": "manual-test@example.com", "password": "test"}

    # Criar usuário
    with httpx.Client(base_url="http://127.0.0.1:8000") as client:
        user_response = client.post("/api/v1/users/", json=user_data)
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

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
