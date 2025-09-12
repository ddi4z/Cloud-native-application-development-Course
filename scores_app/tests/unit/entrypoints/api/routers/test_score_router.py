from src.errors import InvalidSizeError

def test_health_check(client):
    response = client.get("/scores/ping")
    assert response.status_code == 200
    assert response.text == "pong"


def test_calculate_score_invalid_size(client, mocker):
    mock_use_case = mocker.patch(
        "src.entrypoints.api.routers.score_router.build_calculate_score_use_case"
    )
    mock_instance = mock_use_case.return_value
    mock_instance.execute.side_effect = InvalidSizeError("invalid size")

    payload = {
        "offer_id": "offerX",
        "size": "INVALID",
        "amount_offered": 50,
        "baggage_value": 20,
    }

    response = client.post("/scores/", json=payload)
    assert response.status_code == 400
    assert response.text == "" 


def test_calculate_score_multiple_with_invalid(client, mocker):
    mock_use_case = mocker.patch(
        "src.entrypoints.api.routers.score_router.build_calculate_score_use_case"
    )
    mock_instance = mock_use_case.return_value

    mock_instance.execute.side_effect = [100, InvalidSizeError("invalid size")]

    payload = [
        {"offer_id": "offer1", "size": "SMALL", "amount_offered": 100, "baggage_value": 40},
        {"offer_id": "offer2", "size": "INVALID", "amount_offered": 200, "baggage_value": 50},
    ]

    response = client.post("/scores/", json=payload)
    assert response.status_code == 400
