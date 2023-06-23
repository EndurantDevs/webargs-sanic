import json
from http import HTTPStatus

import pytest
from webargs import ValidationError
from sanic import Sanic

from webargs_sanic.sanicparser import HandleValidationError, abort
from .apps.sanic_app import app as myapp


@pytest.fixture
def app():
    return myapp


def test_parsing_view_args(app):
    _, res = app.test_client.get("/echo_view_arg/42")

    assert res.json == {"view_arg": 42}


def test_parsing_invalid_view_arg(app: Sanic):
    _, res = app.test_client.get("/echo_view_arg/foo")

    assert res.status_code == 422
    assert res.content_type == "application/json"
    assert res.json == {'view_args': {'view_arg': ['Not a valid integer.']}}


def test_use_args_with_view_args_parsing(app):
    _, res = app.test_client.get("/echo_view_arg_use_args/42")

    assert res.status_code == HTTPStatus.OK
    assert res.json == {"view_arg": 42}


def test_use_args_on_a_method_view(app):
    _, res = app.test_client.post("/echo_method_view_use_args", params={"val": 42})

    assert res.status_code == HTTPStatus.OK
    assert res.json == {"val": 42}


def test_use_args_on_a_method_view_422(app):
    _, res = app.test_client.post("/echo_method_view_use_args", json={"val": 42})

    assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_use_args_on_a_gather_view(app):
    _, res = app.test_client.post("/echo_lol")

    assert res.json == {'name': 'World'}


def test_use_kwargs_on_a_method_view(app):
    _, res = app.test_client.post("/echo_method_view_use_kwargs", params={"val": 42})

    assert res.status_code == HTTPStatus.OK
    assert res.json == {"val": 42}


def test_use_kwargs_with_missing_data(app):
    _, res = app.test_client.post("/echo_use_kwargs_missing", data={"username": "foo"})

    assert res.json == {"username": "foo"}


def test_invalid_json(app):
    _, res = app.test_client.post(
        "/echo_json",
        json='{"foo": "bar", jdhfjdhjsd}',
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )

    assert res.status_code == 422
    assert res.json == {'json': {'_schema': ['Invalid input type.']}}


# regression test for https://github.com/sloria/webargs/issues/145
def test_nested_many_with_data_key(app):
    _, res = app.test_client.post("/echo_nested_many_data_key", json={"x_field": [{"id": 42}]})
    assert res.status_code == 422

    _, res = app.test_client.post("/echo_nested_many_data_key", json={"X-Field": [{"id": 24}]})
    assert res.status_code == 200
    assert res.json == {"x_field": [{"id": 24}]}

    _, res = app.test_client.post("/echo_nested_many_data_key", json={})
    assert res.status_code == 200
    assert res.json == {}


def test_abort_called_on_validation_error(app):
    _, res = app.test_client.get(
        "/echo_use_args_validated",
        params={"value": 41},
        headers={"Content-Type": "application/json"},
    )

    assert res.status_code == 422
    assert res.json == {'query': {'value': ['Invalid value.']}}


def test_abort_with_message():
    try:
        abort(400, message="custom error message")
    except HandleValidationError as exc:
        assert exc.message == "custom error message"


def test_abort_has_serializable_data():
    try:
        abort(400, message="custom error message")
    except HandleValidationError as err:
        serialized_error = json.dumps(err.data)

        error = json.loads(serialized_error)
        assert isinstance(error, dict)
        assert error["message"] == "custom error message"

    try:
        abort(
            400,
            message="custom error message",
            exc=ValidationError("custom error message"),
        )
    except HandleValidationError as excinfo:
        serialized_error = json.dumps(excinfo.data)
        error = json.loads(serialized_error)
        assert isinstance(error, dict)
        assert error["message"] == "custom error message"
