# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import mock

from sanic.exceptions import SanicException
from sanic import __version__ as sanic_version
from packaging import version

from webargs import fields, ValidationError, missing
from webargs_sanic.sanicparser import parser, abort
from webargs.core import MARSHMALLOW_VERSION_INFO

from .apps.sanic_app import app
from webargs.testing import CommonTestCase
from webtest_sanic import TestApp
import asyncio
import pytest
import io


class TestSanicParser(CommonTestCase):
    def create_app(self):
        return app

    # testing of file uploads is made through sanic.test_client
    # please check test_parse_files function below
    @pytest.mark.skip(reason="files location not supported for aiohttpparser")
    def test_parse_files(self, testapp):
        pass

    def create_testapp(self, app):
        loop = asyncio.get_event_loop()
        self.loop = loop
        return TestApp(app, loop=self.loop)

    def after_create_app(self):
        self.loop.close()

    def test_parsing_view_args(self, testapp):
        res = testapp.get("/echo_view_arg/42")
        assert res.json == {"view_arg": 42}

    def test_parsing_invalid_view_arg(self, testapp):
        res = testapp.get("/echo_view_arg/foo", expect_errors=True)
        assert res.status_code == 422
        assert res.content_type == "application/json"
        assert res.json == {"errors": {"view_arg": ["Not a valid integer."]}}

    def test_use_args_with_view_args_parsing(self, testapp):
        res = testapp.get("/echo_view_arg_use_args/42")
        assert res.json == {"view_arg": 42}

    def test_use_args_on_a_method_view(self, testapp):
        res = testapp.post("/echo_method_view_use_args", {"val": 42})
        assert res.json == {"val": 42}

    def test_use_args_on_a_LOLgather_view(self, testapp):
        res = testapp.post("/echo_lol")
        assert res.json == {'name': 'World'}

    def test_use_kwargs_on_a_method_view(self, testapp):
        res = testapp.post("/echo_method_view_use_kwargs", {"val": 42})
        assert res.json == {"val": 42}

    def test_use_kwargs_with_missing_data(self, testapp):
        res = testapp.post("/echo_use_kwargs_missing", {"username": "foo"}, expect_errors=True)
        assert res.json == {"username": "foo"}

    def test_invalid_json(self, testapp):
        res = testapp.post(
            "/echo",
            '{"foo": "bar", jdhfjdhjsd}',
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            expect_errors=True,
        )
        assert res.status_code == 400
        assert res.json == {'errors': {'json': ['Invalid JSON body.']}}

    # regression test for https://github.com/sloria/webargs/issues/145
    def test_nested_many_with_data_key(self, testapp):
        res = testapp.post_json("/echo_nested_many_data_key", {"x_field": [{"id": 42}]})
        # https://github.com/marshmallow-code/marshmallow/pull/714
        if MARSHMALLOW_VERSION_INFO[0] < 3:
            assert res.json == {"x_field": [{"id": 42}]}

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
    assert abort_kwargs["messages"] == [expected_msg]
    assert type(abort_kwargs["exc"]) == ValidationError


def test_parse_files(loop):

    if (version.parse(sanic_version) < version.parse("19.0.0")):
        res = app.test_client.post(
            "/echo_file", data={"myfile": io.BytesIO(b"data")}, gather_request=False
        )
    else:
        res = app.test_client.post(
            "/echo_file", files=[("myfile", io.BytesIO(b"data"))], gather_request=False
        )
    assert res.json == {"myfile": "data"}


def test_parse_form_returns_missing_if_no_form():
    req = mock.Mock()
    req.form.get.side_effect = AttributeError("no form")
    assert parser.parse_form(req, "foo", fields.Field()) is missing


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
