from sanic.exceptions import NotFound
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
            raise NotFound("Resource not found")

    def update_or_404(self, id, obj):
        try:
            self.storage[id].update(obj)
        except KeyError:
            raise NotFound("Resource not found")

    def get_or_404(self, id):
        try:
            return self.storage[id]
        except KeyError:
            raise NotFound("Resource not found")
