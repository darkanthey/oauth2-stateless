import logging
import os
import signal
import sys
from wsgiref.simple_server import make_server

sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../../'))

from oauth2 import Provider
from oauth2.compatibility import json, parse_qs, urlencode
from oauth2.error import UserNotAuthenticated
from oauth2.grant import ResourceOwnerGrant
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4TokenGenerator
from oauth2.web import ResourceOwnerGrantSiteAdapter
from oauth2.web.wsgi import Application

from multiprocessing import Process
from urllib.request import urlopen
from urllib.error import HTTPError


logging.basicConfig(level=logging.DEBUG)


class ClientApplication(object):
    """
    Very basic application that simulates calls to the API of the
    oauth2-stateless app.
    """
    client_id = "cba"
    client_secret = "zyx"
    token_endpoint = "http://localhost:8081/token"

    LOGIN_TEMPLATE = """<html>
    <body>
        <h1>Test Login</h1>
        <div style="color: red;">
            {failed_message}
        </div>
        <form method="POST" name="confirmation_form" action="/request_token">
            <div>
                Username (foo): <input name="username" type="text" />
            </div>
            <div>
                Password (bar): <input name="password" type="password" />
            </div>
            <div>
                <input type="submit" value="submit" />
            </div>
        </form>
    </body>
</html>"""

    SERVER_ERROR_TEMPLATE = """<html>
    <body>
        <h1>OAuth2 server responded with an error</h1>
        Error type: {error_type}
        Error description: {error_description}
    </body>
</html>"""

    TOKEN_TEMPLATE = """<html>
    <body>
        <div>Access token: {access_token}</div>
        <div>
            <a href="/reset">Reset</a>
        </div>
    </body>
</html>"""

    def __init__(self):
        self.token = None
        self.token_type = ""

    def __call__(self, env, start_response):
        if env["PATH_INFO"] == "/login":
            status, body, headers = self._login(failed=env["QUERY_STRING"] == "failed=1")
        elif env["PATH_INFO"] == "/":
            status, body, headers = self._display_token()
        elif env["PATH_INFO"] == "/request_token":
            status, body, headers = self._request_token(env)
        elif env["PATH_INFO"] == "/reset":
            status, body, headers = self._reset()
        else:
            status = "301 Moved"
            body = ""
            headers = {"Location": "/"}

        start_response(status, [(header, val) for header, val in headers.items()])
        return [body.encode('utf-8')]

    def _display_token(self):
        """
        Display token information or redirect to login prompt if none is
        available.
        """
        if self.token is None:
            return "301 Moved", "", {"Location": "/login"}

        return ("200 OK", self.TOKEN_TEMPLATE.format(access_token=self.token["access_token"]),
                {"Content-Type": "text/html"})

    def _login(self, failed=False):
        """
        Login prompt
        """
        if failed:
            content = self.LOGIN_TEMPLATE.format(failed_message="Login failed")
        else:
            content = self.LOGIN_TEMPLATE.format(failed_message="")
        return "200 OK", content, {"Content-Type": "text/html"}

    def _request_token(self, env):
        """
        Retrieves a new access token from the OAuth2 server.
        """
        params = {}

        content = env['wsgi.input'].read(int(env['CONTENT_LENGTH']))
        post_params = parse_qs(content)
        # Convert to dict for easier access
        for param, value in post_params.items():
            decoded_param = param.decode('utf-8')
            decoded_value = value[0].decode('utf-8')
            if decoded_param == "username" or decoded_param == "password":
                params[decoded_param] = decoded_value

        params["grant_type"] = "password"
        params["client_id"] = self.client_id
        params["client_secret"] = self.client_secret
        # Request an access token by POSTing a request to the auth server.
        try:
            token_result = urlopen(self.token_endpoint, urlencode(params).encode('utf-8'))
            response = token_result.read().decode('utf-8')
        except HTTPError as he:
            if he.code == 400:
                error_body = json.loads(he.read())
                body = self.SERVER_ERROR_TEMPLATE.format(error_type=error_body["error"],
                                                         error_description=error_body["error_description"])
                return "400 Bad Request", body, {"Content-Type": "text/html"}
            if he.code == 401:
                return "302 Found", "", {"Location": "/login?failed=1"}

        self.token = json.loads(response)
        return "301 Moved", "", {"Location": "/"}

    def _reset(self):
        self.token = None
        return "302 Found", "", {"Location": "/login"}


class TestSiteAdapter(ResourceOwnerGrantSiteAdapter):
    def authenticate(self, request, environ, scopes, client):
        example_user_id = 123
        example_ext_data = {}
        username = request.post_param("username")
        password = request.post_param("password")
        # A real world application could connect to a database, try to
        # retrieve username and password and compare them against the input
        if username == "foo" and password == "bar":
            return example_ext_data, example_user_id

        raise UserNotAuthenticated


def run_app_server():
    app = ClientApplication()

    try:
        httpd = make_server('', 8080, app)

        print("Starting Client app on http://localhost:8080/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


def run_auth_server():
    try:
        client_store = ClientStore()
        client_store.add_client(client_id="cba", client_secret=lambda s: s == 'zyx', redirect_uris=[])

        token_store = TokenStore()

        provider = Provider(
            access_token_store=token_store,
            auth_code_store=token_store,
            client_store=client_store,
            token_generator=Uuid4TokenGenerator())

        provider.add_grant(ResourceOwnerGrant(site_adapter=TestSiteAdapter()))

        app = Application(provider=provider)

        httpd = make_server('', 8081, app)

        print("Starting OAuth2 server on http://localhost:8081/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


def main():
    auth_server = Process(target=run_auth_server)
    auth_server.start()
    app_server = Process(target=run_app_server)
    app_server.start()
    print("Visit http://localhost:8080/ in your browser")

    def sigint_handler(signal, frame):
        print("Terminating servers...")
        auth_server.terminate()
        auth_server.join()
        app_server.terminate()
        app_server.join()

    signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    main()
