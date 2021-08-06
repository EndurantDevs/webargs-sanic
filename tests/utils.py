
class TestClient:
    def __init__(self, client):
        self._client = client

    def request(self, method, uri, *args, **kwargs):
        _, response = self._client.request(
            uri, http_method=method, *args, **kwargs
        )
        return response


class SanicTestingTestApp:
    def __init__(self, app):
        self._app = app
        self._client = TestClient(app.test_client)
        self._cookies = {}

    def set_cookie(self, key, value):
        self._cookies[key] = value

    def request(self, method, uri, *args, **kwargs):
        kwargs.pop("expect_errors", None)
        response = self._client.request(
            method, uri, cookies=self._cookies, *args, **kwargs
        )
        return response

    def get(self, uri, *args, **kwargs):
        return self.request("GET", uri, *args, **kwargs)

    def post(self, uri, data=None, content_type=None, *args, **kwargs):
        headers = kwargs.pop('headers', {})
        if content_type:
            headers["content-type"] = content_type
        return self.request("POST", uri, headers=headers, data=data, *args, **kwargs)

    def post_json(self, uri, data=None, *args, **kwargs):
        return self.request("POST", uri, json=data, *args, **kwargs)
