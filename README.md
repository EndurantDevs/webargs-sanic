# webargs-sanic

`webargs-sanic` integrates [webargs](https://github.com/marshmallow-code/webargs) with [Sanic](https://github.com/sanic-org/sanic) so you can parse and validate query params, JSON bodies, forms, headers, cookies, files, and route params in async handlers.

## Compatibility

Current runtime requirements:

- Python `>=3.10`
- `sanic>=25.12,<26`
- `webargs>=8.7,<9`
- `marshmallow>=4.2,<5`

Validated in this repository on:

- Python `3.13.9`
- Python `3.14.3`
- Sanic `25.12.0`
- webargs `8.7.1`
- marshmallow `4.2.3`

## Installation

From PyPI:

```bash
python -m pip install webargs-sanic
```

From source:

```bash
git clone https://github.com/EndurantDevs/webargs-sanic.git
cd webargs-sanic
python -m pip install -e .
```

Optional extras:

- `.[test]` installs the test tooling
- `.[dev]` installs build and lint tooling
- `.[examples]` installs the example app dependencies

## Quickstart

```python
from sanic import Sanic
from sanic.response import text

from webargs import fields, validate
from webargs_sanic.sanicparser import use_args


app = Sanic("demo")

hello_args = {
    "name": fields.Str(required=True, validate=validate.Length(min=3)),
}


@app.get("/")
@use_args(hello_args, location="query")
async def index(request, args):
    return text(f"Hello {args['name']}")
```

## Class-Based Views

```python
from sanic import Sanic
from sanic.response import json
from sanic.views import HTTPMethodView

from webargs import fields
from webargs_sanic.sanicparser import use_args, use_kwargs


app = Sanic("demo")


class EchoMethodViewUseArgs(HTTPMethodView):
    @use_args({"val": fields.Int(required=True)}, location="query")
    async def post(self, request, args):
        return json(args)


class EchoMethodViewUseKwargs(HTTPMethodView):
    @use_kwargs({"val": fields.Int(required=True)}, location="query")
    async def post(self, request, val):
        return json({"val": val})


app.add_route(EchoMethodViewUseArgs.as_view(), "/echo_method_view_use_args")
app.add_route(EchoMethodViewUseKwargs.as_view(), "/echo_method_view_use_kwargs")
```

## Manual Parsing And JSON Errors

```python
from sanic import Sanic
from sanic.response import json

from webargs import fields, validate
from webargs_sanic.sanicparser import HandleValidationError, parser


app = Sanic("demo")


@app.get("/echo_view_args_validated/<value>")
async def echo_use_args_validated(request, value):
    parsed = await parser.parse(
        {"value": fields.Int(required=True, validate=validate.Range(min=43))},
        request,
        location="view_args",
    )
    return json(parsed)


@app.exception(HandleValidationError)
async def handle_validation_error(request, err):
    return json(err.exc.message, status=err.status_code)
```

## Example App

The sample CRUD app lives in `examples/user_simple_storage`.

Install its dependencies with:

```bash
python -m pip install -e ".[examples]"
```

or with:

```bash
python -m pip install -r examples/user_simple_storage/requirements.txt
```

## Testing

This repository uses Sanic's test client and validates the modern dependency stack.

Create dedicated virtualenvs and run the suite:

```bash
python3.13 -m venv .venv313
. .venv313/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
pytest -q
deactivate
```

```bash
python3.14 -m venv .venv314
. .venv314/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
pytest -q
deactivate
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
