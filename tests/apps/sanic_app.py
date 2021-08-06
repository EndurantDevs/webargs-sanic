from sanic import Sanic
from sanic.response import json as J
from sanic.views import HTTPMethodView
from sanic import __version__ as sanic_version
from packaging import version


import marshmallow as ma
from webargs import fields, ValidationError
from webargs_sanic.sanicparser import parser, use_args, use_kwargs, HandleValidationError
#from webargs.core import MARSHMALLOW_VERSION_INFO
import asyncio


class TestAppConfig:
    TESTING = True


hello_args = {"name": fields.Str(missing="World", validate=lambda n: len(n) >= 3)}
hello_multiple = {"name": fields.List(fields.Str())}


class HelloSchema(ma.Schema):
    name = fields.Str(missing="World", validate=lambda n: len(n) >= 3)


strict_kwargs = {} #{"strict": True} if MARSHMALLOW_VERSION_INFO[0] < 3 else {}
hello_many_schema = HelloSchema(many=True, **strict_kwargs)

app = Sanic(__name__.replace('.', '_'))
if (version.parse(sanic_version) < version.parse("20.0.0")):
    app.config.from_object(TestAppConfig)
else:
    app.update_config(TestAppConfig)


@app.route("/echo_lol", methods=["GET", "POST"])
async def echo_lol(request):
    #just FORFUN test
    parsed1 = parser.parse(hello_args, request, location="headers")
    parsed2 = parser.parse(hello_args, request, location="headers")
    parsed3 = parser.parse(hello_args, request, location="headers")
    (res1, res2, res3) = await asyncio.gather(parsed1, parsed2, parsed3)
    return J(res2)


@app.route("/echo", methods=["GET", "POST"])
async def echo(request):
    parsed = await parser.parse(hello_args, request, location="query")
    return J(parsed)


@app.route("/echo_query")
async def echo_query(request):
    parsed = await parser.parse(hello_args, request, location="query")
    return J(parsed)


@app.route("/echo_form", methods=["POST"])
async def echo_form(request):
    parsed = await parser.parse(hello_args, request, location="form")
    return J(parsed)

@app.route("/echo_json", methods=["POST"])
async def echo_json(request):
    parsed = await parser.parse(hello_args, request, location="json")
    return J(parsed)


@app.route("/echo_json_or_form", methods=["POST"])
async def echo_json_or_form(request):
    parsed = await parser.parse(hello_args, request, location="json_or_form")
    return J(parsed)


@app.route("/echo_use_args", methods=["GET", "POST"])
@use_args(hello_args, location="query")
async def echo_use_args(request, args):
    return J(args)


@app.route("/echo_use_args_validated", methods=["POST"])
@use_args(
    {"value": fields.Int()}, validate=lambda args: args["value"] > 42, location="form"
)
async def echo_use_args_validated(request, args):
    return J(args)

@app.route("/echo_use_args_validated", methods=["GET"])
@use_args(
    {"value": fields.Int()}, validate=lambda args: args["value"] > 42, location="query"
)
async def echo_use_args_validated(request, args):
    return J(args)

@app.route("/echo_ignoring_extra_data", methods=["POST"])
async def echo_json_ignore_extra_data(request):
    parsed = await parser.parse(hello_args, request, unknown=ma.EXCLUDE)
    return J(parsed)

@app.route("/echo_use_kwargs", methods=["GET", "POST"])
@use_kwargs(hello_args, location="query")
async def echo_use_kwargs(request, name):
    return J({"name": name})


@app.route("/echo_multi", methods=["GET", "POST"])
async def multi(request):
    parsed = await parser.parse(hello_multiple, request, location="query")
    return J(parsed)


@app.route("/echo_multi_form", methods=["POST"])
async def multi_form(request):
    parsed = await parser.parse(hello_multiple, request, location="form");
    return J(parsed)


@app.route("/echo_multi_json", methods=["POST"])
async def multi_json(request):
    parsed = await parser.parse(hello_multiple, request);
    return J(parsed)


@app.route("/echo_many_schema", methods=["GET", "POST"])
async def many_nested(request):
    parsed = await parser.parse(hello_many_schema, request, location="json")
    return J(parsed, content_type="application/json")


@app.route("/echo_use_args_with_path_param/<name>")
@use_args({"value": fields.Int()}, location="query")
async def echo_use_args_with_path(request, args, name):
    return J(args)


@app.route("/echo_use_kwargs_with_path_param/<name>")
@use_kwargs({"value": fields.Int()}, location="query")
async def echo_use_kwargs_with_path(request, name, value):
    return J({"value": value})


@app.route("/error", methods=["GET", "POST"])
async def error(request):
    def always_fail(value):
        raise ValidationError("something went wrong")

    args = {"text": fields.Str(validate=always_fail)}
    parsed = await parser.parse(args, request)
    return J(parsed)


@app.route("/error400", methods=["GET", "POST"])
async def error400(request):
    def always_fail(value):
        raise ValidationError("something went wrong", status_code=400)

    args = {"text": fields.Str(validate=always_fail)}
    parsed = await parser.parse(args, request)

    return J(parsed)


@app.route("/echo_headers")
async def echo_headers(request):
    parsed1 = parser.parse(hello_args, request, location="headers")
    res1 = await parsed1
    return J(res1)


@app.route("/echo_cookie")
async def echo_cookie(request):
    parsed = await parser.parse(hello_args, request, location="cookies")
    return J(parsed)


@app.route("/echo_file", methods=["POST"])
async def echo_file(request):
    args = {"myfile": fields.Field()}
    result = await parser.parse(args, request, location="files")
    fp = result["myfile"]
    content = fp.body.decode("utf8")
    return J({"myfile": content})


@app.route("/echo_view_arg/<view_arg>")
async def echo_view_arg(request, view_arg):
    parsed = await parser.parse(
        {"view_arg": fields.Int()}, request, location="view_args"
    )
    return J(parsed)


@app.route("/echo_view_arg_use_args/<view_arg>")
@use_args({"view_arg": fields.Int()}, location="view_args")
async def echo_view_arg_with_use_args(request, args, **kwargs):
    return J(args)


@app.route("/echo_nested", methods=["POST"])
async def echo_nested(request):
    args = {"name": fields.Nested({"first": fields.Str(), "last": fields.Str()})}
    parsed = await parser.parse(args, request)
    return J(parsed)


@app.route("/echo_nested_many", methods=["POST"])
async def echo_nested_many(request):
    args = {
        "users": fields.Nested({"id": fields.Int(), "name": fields.Str()}, many=True)
    }
    parsed = await parser.parse(args, request)
    return J(parsed)


@app.route("/echo_nested_many_data_key", methods=["POST"])
async def echo_nested_many_with_data_key(request):
    args = {
        "x_field": fields.Nested({"id": fields.Int()}, many=True, data_key="X-Field")
    }
    parsed = await parser.parse(args, request)
    return J(parsed)


class EchoMethodViewUseArgs(HTTPMethodView):
    @use_args({"val": fields.Int()}, location="query")
    async def post(self, request, args):
        return J(args)


app.add_route(EchoMethodViewUseArgs.as_view(), "/echo_method_view_use_args")


class EchoMethodViewUseKwargs(HTTPMethodView):
    @use_kwargs({"val": fields.Int()}, location="query")
    async def post(self, request, val):
        return J({"val": val})


app.add_route(EchoMethodViewUseKwargs.as_view(), "/echo_method_view_use_kwargs")


@app.route("/echo_use_kwargs_missing", methods=["POST"])
@use_kwargs({"username": fields.Str(required=True), "password": fields.Str()}, location="form")
async def echo_use_kwargs_missing(request, username, **kwargs):
    assert "password" not in kwargs
    return J({"username": username})


# Return validation errors as JSON
@app.exception(HandleValidationError)
async def handle_validation_error(request, err):
    if err.status_code == 422:
        assert isinstance(err.data["schema"], ma.Schema)
    return J(err.exc.messages, status=err.status_code)
