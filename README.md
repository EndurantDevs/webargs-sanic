# webargs-sanic
[Sanic](https://github.com/huge-success/sanic) integration with [Webargs](https://github.com/sloria/webargs)

[![Build Status](https://img.shields.io/travis/EndurantDevs/webargs-sanic.svg?logo=travis)](https://travis-ci.org/EndurantDevs/webargs-sanic) [![Latest Version](https://pypip.in/version/webargs-sanic/badge.svg)](https://pypi.python.org/pypi/webargs-sanic/) [![Python Versions](https://img.shields.io/pypi/pyversions/webargs-sanic.svg)](https://github.com/EndurantDevs/webargs-sanic/blob/master/setup.py) [![Tests Coverage](https://img.shields.io/codecov/c/github/EndurantDevs/webargs-sanic/master.svg)](https://codecov.io/gh/EndurantDevs/webargs-sanic)

[webargs](https://github.com/sloria/webargs) is a Python library for parsing and validating HTTP request arguments, with built-in support for popular web frameworks.

webargs-sanic allows you to use it for [Sanic](https://github.com/huge-success/sanic) apps.

### Example Code ###

```python
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


```

### Installing

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