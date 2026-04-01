import sys
from pathlib import Path
from uuid import uuid4

import pytest


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "user_simple_storage"
if str(EXAMPLE_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_DIR))

import main as example_main  # noqa: E402
from app.views import storage  # noqa: E402


@pytest.fixture
def example_app():
    storage.storage.clear()
    app = example_main.build_app(app_name=f"user_simple_storage_test_{uuid4().hex}")
    yield app
    storage.storage.clear()


def test_healthcheck(example_app):
    _, response = example_app.test_client.get("/healthcheck/")

    assert response.status_code == 200
    assert response.text == "OK"


def test_user_crud_flow(example_app):
    payload = {
        "email": "USER@example.com",
        "password": "supersecret",
        "first_name": "Jane",
        "last_name": "Doe",
        "gender": "F",
        "phone_number": "2025550100",
    }

    _, create_response = example_app.test_client.post("/user/", json=payload)

    assert create_response.status_code == 201
    user_id = create_response.json["user_id"]
    assert len(user_id) == 32

    _, get_response = example_app.test_client.get("/user/", params={"user_id": user_id})

    assert get_response.status_code == 200
    assert get_response.json == {
        **payload,
        "email": "user@example.com",
        "phone_number": "+12025550100",
    }

    _, update_response = example_app.test_client.put(
        "/user/",
        json={"user_id": user_id, "user_data": {"first_name": "Janet"}},
    )

    assert update_response.status_code == 204

    _, get_updated_response = example_app.test_client.get("/user/", params={"user_id": user_id})

    assert get_updated_response.status_code == 200
    assert get_updated_response.json["first_name"] == "Janet"

    _, delete_response = example_app.test_client.delete("/user/", params={"user_id": user_id})

    assert delete_response.status_code == 204

    _, missing_response = example_app.test_client.get("/user/", params={"user_id": user_id})

    assert missing_response.status_code == 404
    assert missing_response.json == {
        "errors": [
            {
                "title": "Resource not found",
                "detail": "Resource not found",
            }
        ]
    }


def test_user_validation_errors(example_app):
    _, invalid_create_response = example_app.test_client.post(
        "/user/",
        json={
            "email": "not-an-email",
            "first_name": "Jane",
            "last_name": "Doe",
            "gender": "X",
        },
    )

    assert invalid_create_response.status_code == 422
    assert invalid_create_response.json == {
        "messages": {
            "json": {
                "email": ["Not a valid email address."],
                "gender": ["Must be one of: M, F."],
            }
        }
    }

    _, invalid_query_response = example_app.test_client.get("/user/", params={"user_id": "short"})

    assert invalid_query_response.status_code == 422
    assert invalid_query_response.json == {
        "messages": {
            "query": {
                "user_id": ["Length must be 32."]
            }
        }
    }
