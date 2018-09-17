from sanic import response
from sanic import Blueprint
from webargs_sanic.sanicparser import use_args
from webargs_sanic.sanicparser import use_kwargs
from app.fields import user_data
from app.fields import user_id
from app.fields import user_update
from app.storage import InMemory

blueprint = Blueprint('app')
storage = InMemory()


@blueprint.route('/healthcheck/')
async def healthcheck(request):
    return response.text('OK')


@blueprint.post('/user/')
@use_args(user_data)
async def add_user(request, args):
    return response.json({"user_id":storage.insert(args)}, status=201)


@blueprint.get('/user/')
@use_kwargs(user_id)
async def get_user(request, user_id):
    return response.json(storage.get_or_404(user_id))


@blueprint.put('/user/')
@use_kwargs(user_update)
async def update_user(request, user_id, user_data):
    storage.update_or_404(user_id, user_data)
    return response.text('', status=204)


@blueprint.delete('/user/')
@use_kwargs(user_id)
async def get_user(request, user_id):
    storage.delete_or_404(user_id)
    return response.text('', status=204)
