# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import mock
import asyncio

from sanic.exceptions import SanicException
from sanic import __version__ as sanic_version
from packaging import version

from webargs import ValidationError
from webargs_sanic.sanicparser import abort
from webargs.testing import CommonTestCase
from sanic.server import serve, HttpProtocol

from .apps.sanic_app import app
import pytest
import io


class TestSanicParser(CommonTestCase):
    def create_app(self):
        return app

    def create_testapp(self, app):
        if (version.parse(sanic_version) < version.parse("21.0.0")):
            from webtest_sanic import TestApp

            loop = asyncio.get_event_loop()
            self.loop = loop
            return TestApp(app, loop=self.loop)
        else:
            from .utils import SanicTestingTestApp

            return SanicTestingTestApp(app)

    # testing of file uploads is made through sanic.test_client
    # please check test_parse_files function below
    @pytest.mark.skip(reason="files location not supported for aiohttpparser")
    def test_parse_files(self, testapp):
        pass

    def test_parsing_view_args(self, testapp):
        res = testapp.get("/echo_view_arg/42")
        assert res.json == {"view_arg": 42}

    def test_parsing_invalid_view_arg(self, testapp):
        res = testapp.get("/echo_view_arg/foo", expect_errors=True)
        assert res.status_code == 422
        assert res.content_type == "application/json"
        assert res.json == {'view_args': {'view_arg': ['Not a valid integer.']}}

    def test_use_args_with_view_args_parsing(self, testapp):
        res = testapp.get("/echo_view_arg_use_args/42")
        assert res.json == {"view_arg": 42}

    def test_use_args_on_a_method_view(self, testapp):
        res = testapp.post("/echo_method_view_use_args", params={"val": 42})
        assert res.json == {"val": 42}

    def test_use_args_on_a_LOLgather_view(self, testapp):
        res = testapp.post("/echo_lol")
        assert res.json == {'name': 'World'}

    def test_use_kwargs_on_a_method_view(self, testapp):
        res = testapp.post("/echo_method_view_use_kwargs", params={"val": 42})
        assert res.json == {"val": 42}

    def test_use_kwargs_with_missing_data(self, testapp):
        res = testapp.post("/echo_use_kwargs_missing", {"username": "foo"})
        assert res.json == {"username": "foo"}

    def test_invalid_json(self, testapp):
        res = testapp.post(
            "/echo_json",
            '{"foo": "bar", jdhfjdhjsd}',
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            expect_errors=True
        )
        assert res.status_code == 400
        assert res.json == {'json': ['Invalid JSON body.']}

    # regression test for https://github.com/sloria/webargs/issues/145
    def test_nested_many_with_data_key(self, testapp):
        post_with_raw_fieldname_args = (
            "/echo_nested_many_data_key",
            {"x_field": [{"id": 42}]},
        )
        res = testapp.post_json(*post_with_raw_fieldname_args, expect_errors=True)
        assert res.status_code == 422

        res = testapp.post_json("/echo_nested_many_data_key", {"X-Field": [{"id": 24}]})
        assert res.json == {"x_field": [{"id": 24}]}

        res = testapp.post_json("/echo_nested_many_data_key", {})
        assert res.json == {}


@mock.patch("webargs_sanic.sanicparser.abort")
def test_abort_called_on_validation_error(mock_abort, loop):
    app.test_client.get(
        "/echo_use_args_validated",
        params={"value": 41},
        headers={"content_type": "application/json"},
    )

    mock_abort.assert_called()
    abort_args, abort_kwargs = mock_abort.call_args
    assert abort_args[0] == 422
    expected_msg = "Invalid value."
    assert abort_kwargs["messages"]["query"] == [expected_msg]
    assert type(abort_kwargs["exc"]) == ValidationError




def test_parse_files(loop):
    print(version.parse(sanic_version))
    if (version.parse(sanic_version) < version.parse("19.0.0")):
        _, res = app.test_client.post(
            "/echo_file", data={"myfile": io.BytesIO(b"data")}
        )
    else:
        _, res = app.test_client.post(
        "/echo_file", files=[("myfile", io.BytesIO(b"data"))]
    )

    assert res.json == {"myfile": "data"}


def test_abort_with_message():
    with pytest.raises(SanicException) as excinfo:
        abort(400, message="custom error message")
    assert excinfo.value.data["message"] == "custom error message"


def test_abort_has_serializable_data():
    with pytest.raises(SanicException) as excinfo:
        abort(400, message="custom error message")
    serialized_error = json.dumps(excinfo.value.data)
    error = json.loads(serialized_error)
    assert isinstance(error, dict)
    assert error["message"] == "custom error message"

    with pytest.raises(SanicException) as excinfo:
        abort(
            400,
            message="custom error message",
            exc=ValidationError("custom error message"),
        )
    serialized_error = json.dumps(excinfo.value.data)
    error = json.loads(serialized_error)
    assert isinstance(error, dict)
    assert error["message"] == "custom error message"
