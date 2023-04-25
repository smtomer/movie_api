from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


# Valid tesst
def test_add_conversation_passing_1():
    test = {
        "character_1_id": 0,
        "character_2_id": 2,
        "lines": [
            {
                "character_id": 0,
                "line_text": "If you can see this then the test passed."
            }
        ]
    }
    response = client.post("/movies/0/conversations/", json=test)
    assert response.status_code == 200


# Identical characters error
def test_add_conversation_identical_error():
    test = {
        "character_1_id": 0,
        "character_2_id": 0,
        "lines": [
            {
                "character_id": 0,
                "line_text": "test"
            }
        ]
    }
    response = client.post("/movies/0/conversations/", json=test)
    assert response.status_code == 404