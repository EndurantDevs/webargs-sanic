# -*- coding: utf-8 -*-
"""Sanic request argument parsing module.

Example: ::

    from sanic import Sanic

    from webargs import fields
    from webargs_sanic.sanicparser import use_args

    app = Sanic(__name__)

    hello_args = {
        'name': fields.Str(required=True)
    }

    @app.route('/')
    @use_args(hello_args)
    async def index(args):
        return 'Hello ' + args['name']
"""
import contextlib
import typing
import sanic
from sanic.request import Request
from sanic.exceptions import InvalidUsage

from webargs import core
from webargs.asyncparser import AsyncParser
from webargs.multidictproxy import MultiDictProxy
from marshmallow import Schema, RAISE, ValidationError

from functools import singledispatch


@singledispatch
def keys_to_strings(ob):
    return ob


@keys_to_strings.register
def _handle_dict(ob: dict):
    return {str(k): keys_to_strings(v) for k, v in ob.items()}


@keys_to_strings.register
def _handle_list(ob: list):
    return [keys_to_strings(v) for v in ob]


@keys_to_strings.register
def _handle_list(ob: ValueError):
    return str(ob)


class HandleValidationError(sanic.exceptions.SanicException):
    """Define default status code to process"""

    status_code = 422
    quiet = True
    exc = None
    message = None
    data = None
    schema = None
    error_headers = None


def abort(http_status_code, exc=None, **kwargs):
    """Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.

    From Flask-Restful. See NOTICE file for license information.
    """

    if kwargs.get('message'):
        message = kwargs.get('message')
    else:
        if exc and hasattr(exc, 'message'):
            message = exc.message
        elif exc and hasattr(exc, 'messages'):
            message = exc.messages
        else:
            message = "{'validation_error': 'no message defined'}"

    err = HandleValidationError(status_code=http_status_code, message=message)
    err.exc = exc or err
    if not isinstance(err.exc, str):
        err.exc.message = message
    err.data = kwargs
    if kwargs.get('schema'):
        err.schema = kwargs.get('schema')

    if kwargs.get('error_headers'):
        err.error_headers = kwargs.get('error_headers')
    raise err


def is_json_request(req):
    """check the validity of json via core functionality"""
    content_type = req.content_type
    return core.is_json(content_type)


class SanicParser(AsyncParser):
    """Sanic request argument parser."""

    DEFAULT_UNKNOWN_BY_LOCATION = {
        "view_args": RAISE,
        "match_info": RAISE,
        "path": RAISE,
        **core.Parser.DEFAULT_UNKNOWN_BY_LOCATION,
    }
    __location_map__ = dict(
        view_args="load_view_args",
        path="load_view_args",
        **core.Parser.__location_map__,
    )

    def load_json_or_form(
        self, req, schema: Schema,
    ) -> typing.Union[typing.Dict, MultiDictProxy]:
        data = self.load_json(req, schema)
        if data is not core.missing:
            return data
        return self.load_form(req, schema)

    def load_json(self, req, schema: Schema):
        """Return a parsed json payload from the request."""
        if not (req.body and is_json_request(req)):
            return core.missing

        try:
            json_data = req.load_json()
        except (UnicodeDecodeError, InvalidUsage, ValueError) as json_exception:
            self._handle_invalid_json_error(json_exception, req, schema)

        return json_data

    def load_match_info(self, req, schema: Schema) -> typing.Mapping:
        """Load the request's ``match_info``."""
        # pylint: disable=unused-argument, no-self-use
        return req.match_info

    def get_request_from_view_args(
            self, view: typing.Callable, args: typing.Iterable, kwargs: typing.Mapping
    ):
        """Get request object from a handler function or method. Used internally by
        ``use_args`` and ``use_kwargs``.
        """
        req = next((arg for arg in args if isinstance(arg, Request)), None)
        if not isinstance(req, Request):
            raise ValueError("Request argument not found for handler")
        return req

    def load_view_args(self, req, schema):
        """Return the request's ``view_args`` or ``missing`` if there are none."""
        # pylint: disable=no-self-use
        return MultiDictProxy(req.match_info, schema) or core.missing

    def load_querystring(self, req, schema):
        """Return query params from the request as a MultiDictProxy."""
        return MultiDictProxy(req.args, schema)

    def load_form(self, req, schema):
        """Return form values from the request as a MultiDictProxy."""
        with contextlib.suppress(AttributeError):
            return MultiDictProxy(req.form, schema)
        return core.missing

    def load_headers(self, req, schema):
        """Return headers from the request as a MultiDictProxy."""
        return MultiDictProxy(req.headers, schema)

    def load_cookies(self, req, schema):
        """Return cookies from the request."""
        return req.cookies

    def load_files(self, req, schema):
        """Return files from the request as a MultiDictProxy."""
        return MultiDictProxy(req.files, schema)

    def handle_error(
            self,
            error: ValidationError,
            req,
            schema: Schema,
            *,
            error_status_code: typing.Optional[int],
            error_headers: typing.Optional[typing.Mapping[str, str]]
    ) -> typing.NoReturn:
        """Handles errors during parsing. Aborts the current HTTP request and
        responds with a 422 error.
        """
        status_code = error_status_code or getattr(
            error, "status_code", self.DEFAULT_VALIDATION_STATUS,
        )
        error.messages = keys_to_strings(error.messages)
        abort(status_code, exc=error, message=error.messages,
              schema=schema, status_code=status_code, error_headers=error_headers, req=req)

    def _handle_invalid_json_error(
            self,
            error: typing.Union[UnicodeDecodeError, InvalidUsage, ValueError],
            req,
            *args,
            **kwargs
    ) -> typing.NoReturn:
        http_status_code=400
        abort(http_status_code, exc=error, message={"json": ["Invalid JSON body."]},
              status_code=http_status_code, req=req)


parser = SanicParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
