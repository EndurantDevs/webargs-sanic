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
import sanic
from sanic.request import Request
from sanic.exceptions import InvalidUsage

import typing
import json

from webargs import core
from webargs.asyncparser import AsyncParser
from webargs.core import json as wa_json
from webargs.multidictproxy import MultiDictProxy
from marshmallow import Schema, ValidationError, RAISE

@sanic.exceptions.add_status_code(400)
@sanic.exceptions.add_status_code(422)
class HandleValidationError(sanic.exceptions.SanicException):
    pass


def abort(http_status_code, exc=None, **kwargs):
    """Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.

    From Flask-Restful. See NOTICE file for license information.
    """
    try:
        sanic.exceptions.abort(http_status_code, exc)
    except sanic.exceptions.SanicException as err:
        err.data = kwargs

        if exc and not hasattr(exc, 'messages'):
            exc.messages = kwargs.get('messages')
        err.exc = exc
        raise err


def is_json_request(req):
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
    __location_map__ = dict(view_args="load_view_args", path="load_view_args", **core.Parser.__location_map__)


    async def load_json_or_form(
        self, req, schema: Schema
    ) -> typing.Union[typing.Dict, MultiDictProxy]:
        data = await self.load_json(req, schema)
        if data is not core.missing:
            return data
        return await self.load_form(req, schema)

    async def load_json(self, req, schema: Schema):
        """Return a parsed json payload from the request."""
        if not (req.body and is_json_request(req)):
            return core.missing

        try:
            json_data = req.load_json()
        except InvalidUsage as e:
            return self._handle_invalid_json_error(e, req)
        except UnicodeDecodeError as e:
            return self._handle_invalid_json_error(e, req)

        return json_data

    def load_match_info(self, req, schema: Schema) -> typing.Mapping:
        """Load the request's ``match_info``."""
        return req.match_info

    def get_request_from_view_args(
            self, view: typing.Callable, args: typing.Iterable, kwargs: typing.Mapping
    ):
        """Get request object from a handler function or method. Used internally by
        ``use_args`` and ``use_kwargs``.
        """
        req = None
        for arg in args:
            if isinstance(arg, Request):
                req = arg
                break
        if not isinstance(req, Request):
            raise ValueError("Request argument not found for handler")
        return req

    def load_view_args(self, req, schema):
        """Return the request's ``view_args`` or ``missing`` if there are none."""
        return MultiDictProxy(req.match_info, schema) or core.missing

    def load_querystring(self, req, schema):
        """Return query params from the request as a MultiDictProxy."""
        return MultiDictProxy(req.args, schema)

    async def load_form(self, req, schema):
        """Return form values from the request as a MultiDictProxy."""
        try:
            return MultiDictProxy(req.form, schema)
        except AttributeError:
            pass
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


    def handle_error(self, error, req, schema, error_status_code=None, error_headers=None):
        """Handles errors during parsing. Aborts the current HTTP request and
        responds with a 422 error.
        """
        status_code = error_status_code or getattr(error, "status_code", self.DEFAULT_VALIDATION_STATUS)
        abort(status_code, exc=error, messages=error.messages, schema=schema, status_code=status_code)

    def _handle_invalid_json_error(self, error, req, *args, **kwargs):
        status_code=400
        abort(status_code, exc=error, messages={"json": ["Invalid JSON body."]}, status_code=status_code)



parser = SanicParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
