def test_create_concept(client, neo4j_driver):
    response = client.post(
        "/api/v1/concepts/",
        json={"name": "Soma", "description": "Operação matemática básica"},
    )
    # A rota agora é protegida, deve retornar 401
    assert response.status_code == 401
