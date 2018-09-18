from http import HTTPStatus

from sanic import Blueprint
from sanic.exceptions import NotFound
from sanic.response import json
from webargs_sanic.sanicparser import HandleValidationError

from extentions.helpers import format_error
from extentions.helpers import return_an_error


blueprint = Blueprint('extentions.exceptions')

@blueprint.exception(NotFound)
def handle_404(request, exception):
    '''Handle 404 Not Found
    This handler should be used to handle error http 404 not found for all
    endpoints or if resource not available.
    '''
    error = format_error(title='Resource not found', detail=str(exception))
    return json(return_an_error(error), status=HTTPStatus.NOT_FOUND)


@blueprint.exception(HandleValidationError)
def handle_422(request, exception):
    error = {"messages": exception.exc.messages}
    return json(error, status=HTTPStatus.UNPROCESSABLE_ENTITY)
