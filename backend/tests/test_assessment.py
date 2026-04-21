def test_get_assessment(client):
    response = client.get("/api/v1/assessment")
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) == 9
