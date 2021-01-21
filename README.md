# webargs-sanic
[Sanic](https://github.com/huge-success/sanic) integration with [Webargs](https://github.com/sloria/webargs). 

Parsing and validating request arguments: headers, arguments, cookies, files, json, etc.

IMPORTANT: From version 2.0.0 webargs-sanic requires you to have webargs >=7.0.1. Please be aware of changes happened in version of webargs > 6.0.0. If you need support of webargs 5.x with no location definition, please use previous version(1.5.0) of this module from pypi. 

[![Build Status](https://img.shields.io/travis/EndurantDevs/webargs-sanic.svg?logo=travis)](https://travis-ci.org/EndurantDevs/webargs-sanic) [![Latest Version](https://img.shields.io/pypi/v/webargs-sanic.svg)](https://pypi.python.org/pypi/webargs-sanic/) [![Python Versions](https://img.shields.io/pypi/pyversions/webargs-sanic.svg)](https://github.com/EndurantDevs/webargs-sanic/blob/master/setup.py) [![Tests Coverage](https://img.shields.io/codecov/c/github/EndurantDevs/webargs-sanic/master.svg)](https://codecov.io/gh/EndurantDevs/webargs-sanic)

[webargs](https://github.com/sloria/webargs) is a Python library for parsing and validating HTTP request arguments, with built-in support for popular web frameworks. webargs-sanic allows you to use it for [Sanic](https://github.com/huge-success/sanic) apps. To read more about webargs usage, please check [Quickstart](https://webargs.readthedocs.io/en/latest/quickstart.html)

## Example Code ##

### Simple Application ###
```python
from sanic import Sanic
from sanic.response import text

from webargs import fields
from webargs_sanic.sanicparser import use_args


app = Sanic(__name__)

hello_args = {
    'name': fields.Str(required=True)
}

@app.route('/')
@use_args(hello_args, location="query")
async def index(request, args):
    return text('Hello ' + args['name'])


```

### Class-based Sanic app and args/kwargs ###

```python
from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import json

from webargs import fields
from webargs_sanic.sanicparser import use_args, use_kwargs


app = Sanic(__name__)

class EchoMethodViewUseArgs(HTTPMethodView):
    @use_args({"val": fields.Int()}, location="form")
    async def post(self, request, args):
        return json(args)


app.add_route(EchoMethodViewUseArgs.as_view(), "/echo_method_view_use_args")


class EchoMethodViewUseKwargs(HTTPMethodView):
    @use_kwargs({"val": fields.Int()}, location="query")
    async def post(self, request, val):
        return json({"val": val})


app.add_route(EchoMethodViewUseKwargs.as_view(), "/echo_method_view_use_kwargs")
```

### Parser without decorator with returning errors as JSON ###
```python
from sanic import Sanic
from sanic.response import json

from webargs import fields
from webargs_sanic.sanicparser import parser, HandleValidationError

app = Sanic(__name__)

@app.route("/echo_view_args_validated/<value>", methods=["GET"])
async def echo_use_args_validated(request, args):
    parsed = await parser.parse(
        {"value": fields.Int(required=True, validate=lambda args: args["value"] > 42)}, request, location="view_args"
    )
    return json(parsed)


# Return validation errors as JSON
@app.exception(HandleValidationError)
async def handle_validation_error(request, err):
    return json({"errors": err.exc.messages}, status=422)
```

### More complicated custom example ###
```python
from sanic import Sanic
from sanic import response
from sanic import Blueprint

from webargs_sanic.sanicparser import use_kwargs

from some_CUSTOM_storage import InMemory

from webargs import fields
from webargs import validate

import marshmallow.fields
from validate_email import validate_email

#usually this should not be here, better to import ;)
#please check examples for more info
class Email(marshmallow.fields.Field):

    def __init__(self, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)

    def _deserialize(self, value, attr, obj):
        value = value.strip().lower()
        if not validate_email(value):
            self.fail('validator_failed')
        return value

user_update = {
    'user_data': fields.Nested({
        'email': Email(),
        'password': fields.Str(validate=lambda value: len(value)>=8),
        'first_name': fields.Str(validate=lambda value: len(value)>=1),
        'last_name': fields.Str(validate=lambda value: len(value)>=1),
        'middle_name': fields.Str(),
        'gender': fields.Str(validate=validate.OneOf(["M", "F"])),
        'birth_date': fields.Date(),
    }),
    'user_id': fields.Str(required=True, validate=lambda x:len(x)==32),
}


blueprint = Blueprint('app')
storage = InMemory()


@blueprint.put('/user/')
@use_kwargs(user_update, location="json_or_form")
async def update_user(request, user_id, user_data):
    storage.update_or_404(user_id, user_data)
    return response.text('', status=204)

app = Sanic(__name__)
app.blueprint(blueprint, url_prefix='/')

```

For more examples and checking how to use custom validations (phones, emails, etc.) please check apps in [Examples](https://github.com/EndurantDevs/webargs-sanic/tree/master/examples/)

## Installing ##

It is easy to do from `pip`

```
pip install webargs-sanic
```

or from sources

```
git clone git@github.com:EndurantDevs/webtest-sanic.git
cd webtest-sanic
python setup.py install
```

## Running the tests

Project uses common tests from webargs package. Thanks to [Steven Loria](https://github.com/sloria) for [sharing tests in webargs v4.1.0](https://github.com/sloria/webargs/pull/287#issuecomment-422232384). 
Most of tests are run by webtest via [webtest-sanic](https://github.com/EndurantDevs/webtest-sanic). 
Some own tests get run via Sanic's TestClient.

To be sure everything is fine before installation from sources, just run:
```bash
pip -r requirements.txt
```
and then
```bash
python setup.py test
```
Or
```bash
pytest tests/
```


## Authors
[<img src="https://github.com/EndurantDevs/botstat-seo/raw/master/docs/img/EndurantDevs-big.png" alt="Endurant Developers Python Team" width="150">](https://www.EndurantDev.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
