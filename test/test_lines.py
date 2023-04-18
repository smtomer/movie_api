from fastapi.testclient import TestClient
from src.api.server import app
import json

client = TestClient(app)

def test_get_line():
    response = client.get("/lines/1")
    assert response.status_code == 200

    with open("test/lines/1.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_conversation_lines():
    # Test for an existing conversation
    response = client.get("/conversations/5/lines")
    assert response.status_code == 200

    with open("test/lines/conversation-5-lines.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_character_lines():
    # Test for an existing character
    response = client.get("/characters/10/lines")
    assert response.status_code == 200

    with open("test/lines/character-10-lines.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)
