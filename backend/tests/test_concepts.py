def test_create_concept(client, neo4j_driver):
    response = client.post(
        "/api/v1/concepts/",
        json={"name": "Soma", "description": "Operação matemática básica"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Soma"
