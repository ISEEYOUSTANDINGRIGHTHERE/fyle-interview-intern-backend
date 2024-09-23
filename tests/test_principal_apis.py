def test_principal_can_regrade_assignment(client, principal_headers):
    # Arrange
    payload = {"id": 1, "grade": "B+"}

    # Act
    response = client.post('/principal/assignments/grade', json=payload, headers=principal_headers)

    # Assert
    assert response.status_code == 200
    assert response.json['data']['grade'] == "B+"
