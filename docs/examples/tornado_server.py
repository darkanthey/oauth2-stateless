import logging
import os
import signal
import sys
from wsgiref.simple_server import WSGIRequestHandler, make_server

sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../../'))

from oauth2 import Provider
from oauth2.compatibility import json, parse_qs, urlencode
from oauth2.error import UserNotAuthenticated
from oauth2.grant import AuthorizationCodeGrant
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4TokenGenerator
from oauth2.web import AuthorizationCodeGrantSiteAdapter
from oauth2.web.tornado import OAuth2Handler
from tornado.ioloop import IOLoop
from tornado.web import Application, url

if sys.version_info >= (3, 0):
    from multiprocessing import Process
    from urllib.request import urlopen
else:
    from multiprocessing.process import Process
    from urllib2 import urlopen

logging.basicConfig(level=logging.DEBUG)


class ClientRequestHandler(WSGIRequestHandler):
    """
    Request handler that enables formatting of the log messages on the console.

    This handler is used by the client application.
    """
    def address_string(self):
        return "client app"


class OAuthRequestHandler(WSGIRequestHandler):
    """
    Request handler that enables formatting of the log messages on the console.

    This handler is used by the oauth2-stateless application.
    """
    def address_string(self):
        return "oauth2-stateless"


class TestSiteAdapter(AuthorizationCodeGrantSiteAdapter):
    """
    This adapter renders a confirmation page so the user can confirm the auth
    request.
    """

    CONFIRMATION_TEMPLATE = """
<html>
    <body>
        <p>
            <a href="{url}&confirm=1">confirm</a>
        </p>
        <p>
            <a href="{url}&confirm=0">deny</a>
        </p>
    </body>
</html>
    """

    def render_auth_page(self, request, response, environ, scopes, client):
        page_url = request.path + "?" + request.query_string
        response.body = self.CONFIRMATION_TEMPLATE.format(url=page_url)

        return response

    def authenticate(self, request, environ, scopes, client):
        if request.method == "GET":
            if request.get_param("confirm") == "1":
                return
        raise UserNotAuthenticated

    def user_has_denied_access(self, request):
        if request.method == "GET":
            if request.get_param("confirm") == "0":
                return True
        return False


class ClientApplication(object):
    """
    Very basic application that simulates calls to the API of the
    oauth2-stateless app.
    """
    callback_url = "http://localhost:8080/callback"
    client_id = "abc"
    client_secret = "xyz"
    api_server_url = "http://localhost:8081"

    def __init__(self):
        self.access_token_result = None
        self.access_token = None
        self.auth_token = None
        self.token_type = ""

    def __call__(self, env, start_response):
        if env["PATH_INFO"] == "/app":
            status, body, headers = self._serve_application(env)
        elif env["PATH_INFO"] == "/callback":
            status, body, headers = self._read_auth_token(env)
        else:
            status = "301 Moved"
            body = ""
            headers = {"Location": "/app"}

        start_response(status, [(header, val) for header, val in headers.items()])
        return [body.encode('utf-8')]

    def _request_access_token(self):
        print("Requesting access token...")

        post_params = {"client_id": self.client_id,
                       "client_secret": self.client_secret,
                       "code": self.auth_token,
                       "grant_type": "authorization_code",
                       "redirect_uri": self.callback_url}
        token_endpoint = self.api_server_url + "/token"

        token_result = urlopen(token_endpoint, urlencode(post_params).encode('utf-8'))
        result = json.loads(token_result.read().decode('utf-8'))

        self.access_token_result = result
        self.access_token = result["access_token"]
        self.token_type = result["token_type"]

        confirmation = "Received access token '%s' of type '%s'" % (self.access_token, self.token_type)
        print(confirmation)
        return "302 Found", "", {"Location": "/app"}

    def _read_auth_token(self, env):
        print("Receiving authorization token...")

        query_params = parse_qs(env["QUERY_STRING"])

        if "error" in query_params:
            location = "/app?error=" + query_params["error"][0]
            return "302 Found", "", {"Location": location}

        self.auth_token = query_params["code"][0]

        print("Received temporary authorization token '%s'" % (self.auth_token,))
        return "302 Found", "", {"Location": "/app"}

    def _request_auth_token(self):
        print("Requesting authorization token...")

        auth_endpoint = self.api_server_url + "/authorize"
        query = urlencode({"client_id": "abc",
                           "redirect_uri": self.callback_url,
                           "response_type": "code"})

        location = "%s?%s" % (auth_endpoint, query)
        return "302 Found", "", {"Location": location}

    def _serve_application(self, env):
        query_params = parse_qs(env["QUERY_STRING"])
        if ("error" in query_params and query_params["error"][0] == "access_denied"):
            return "200 OK", "User has denied access", {}

        if self.access_token_result is None:
            if self.auth_token is None:
                return self._request_auth_token()
            return self._request_access_token()
        confirmation = "Current access token '%s' of type '%s'" % (self.access_token, self.token_type)
        return "200 OK", str(confirmation), {}


def run_app_server():
    app = ClientApplication()

    try:
        httpd = make_server('', 8080, app, handler_class=ClientRequestHandler)

        print("Starting Client app on http://localhost:8080/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


def run_auth_server():
    client_store = ClientStore()
    client_store.add_client(client_id="abc", client_secret="xyz", redirect_uris=["http://localhost:8080/callback"])

    token_store = TokenStore()

    provider = Provider(access_token_store=token_store,
                        auth_code_store=token_store, client_store=client_store,
                        token_generator=Uuid4TokenGenerator())
    provider.add_grant(AuthorizationCodeGrant(site_adapter=TestSiteAdapter()))

    try:
        app = Application([
            url(provider.authorize_path, OAuth2Handler, dict(provider=provider)),
            url(provider.token_path, OAuth2Handler, dict(provider=provider)),
        ])

        app.listen(8081)
        print("Starting OAuth2 server on http://localhost:8081/...")
        IOLoop.current().start()
    except KeyboardInterrupt:
        IOLoop.close()

def main():
    auth_server = Process(target=run_auth_server)
    auth_server.start()
    app_server = Process(target=run_app_server)
    app_server.start()
    print("Access http://localhost:8080/app in your browser")

    def sigint_handler(signal, frame):
        print("Terminating servers...")
        auth_server.terminate()
        auth_server.join()
        app_server.terminate()
        app_server.join()

    signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    main()
