from sanic.exceptions import abort
from uuid import uuid4


class InMemory(object):

    def __init__(self):
        self.storage = {}

    def insert(self, obj):
        id = uuid4().hex
        self.storage[id] = obj
        return id

    def delete_or_404(self, id):
        try:
            self.storage.pop(id)
        except KeyError:
            abort(404)

    def update_or_404(self, id, obj):
        try:
            self.storage[id].update(obj)
        except KeyError:
            abort(404)

    def get_or_404(self, id):
        try:
            return self.storage[id]
        except KeyError:
            abort(404)
