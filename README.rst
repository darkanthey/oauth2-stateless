oauth2-stateless
#############

oauth2-stateless is a framework that aims at making it easy to provide authentication
via `OAuth 2.0 <http://tools.ietf.org/html/rfc6749>`_ within an application stack.
Main difference of this library is the simplicity
and the ability to work without any database just with 'stateless'
tokens based on JWT (JSON Web Tokens).


`Documentation <http://oauth2-stateless.readthedocs.org/en/latest/index.html>`_

Status
******

oauth2-stateless has reached its beta phase. All main parts of the `OAuth 2.0 RFC <http://tools.ietf.org/html/rfc6749>`_ such as the various types of Grants, Refresh Token and Scopes have been implemented.

Installation
************

oauth2-stateless is available on
`PyPI <http://pypi.python.org/pypi/oauth2-stateless/>`_.

    pip install oauth2-stateless


Usage
*****

Example Authorization server

.. code-block:: python

    from wsgiref.simple_server import make_server
    import oauth2
    import oauth2.grant
    import oauth2.error
    from oauth2.store.memory import ClientStore
    from oauth2.store.stateless import Token Store
    import oauth2.tokengenerator
    import oauth2.web.wsgi


    # Create a SiteAdapter to interact with the user.
    # This can be used to display confirmation dialogs and the like.
    class ExampleSiteAdapter(oauth2.web.AuthorizationCodeGrantSiteAdapter, oauth2.web.ImplicitGrantSiteAdapter):
        TEMPLATE = '''
    <html>
        <body>
            <p>
                <a href="{url}&confirm=confirm">confirm</a>
            </p>
            <p>
                <a href="{url}&deny=deny">deny</a>
            </p>
        </body>
    </html>'''

        def authenticate(self, request, environ, scopes, client):
            # Check if the user has granted access
            if request.post_param("confirm") == "confirm":
                return {}

            raise oauth2.error.UserNotAuthenticated

        def render_auth_page(self, request, response, environ, scopes, client):
            url = request.path + "?" + request.query_string
            response.body = self.TEMPLATE.format(url=url)
            return response

        def user_has_denied_access(self, request):
            # Check if the user has denied access
            if request.post_param("deny") == "deny":
                return True
            return False

    # Create an in-memory storage to store your client apps.
    client_store = ClientStore()
    # Add a client
    client_store.add_client(client_id="abc", client_secret="xyz", redirect_uris=["http://localhost/callback"])

    site_adapter = ExampleSiteAdapter()

    # Create an in-memory storage to store issued tokens.
    # LocalTokenStore can store access and auth tokens
    stateless_token = oauth2.tokengenerator.StatelessTokenGenerator(secret_key='xxx')
    token_store = TokenStore(stateless)

    # Create the controller.
    provider = oauth2.Provider(
        access_token_store=token_store,
        auth_code_store=token_store,
        client_store=client_store,
        token_generator=stateless_token)
    )

    # Add Grants you want to support
    provider.add_grant(oauth2.grant.AuthorizationCodeGrant(site_adapter=site_adapter))
    provider.add_grant(oauth2.grant.ImplicitGrant(site_adapter=site_adapter))

    # Add refresh token capability and set expiration time of access tokens to 30 days
    provider.add_grant(oauth2.grant.RefreshToken(expires_in=2592000))

    # Wrap the controller with the Wsgi adapter
    app = oauth2.web.wsgi.Application(provider=provider)

    if __name__ == "__main__":
        httpd = make_server('', 8080, app)
        httpd.serve_forever()


This example only shows how to instantiate the server.
It is not a working example as a client app is missing.
Take a look at the `examples <docs/examples/>`_ directory.

Or just run this example:
python docs/examples/stateless_client_server.py

This is already a workable example. They can work without database
because oauth token already contain all the necessary information like
a user_id, grant_type, data, scopes and client_id.
If you want to check user state like a ban, disable, etc.
You can check this param on server site from database. By adding this check to
/api/me or redefine oauth2.tokengenerator and add specific logic.


Supported storage backends
**************************

oauth2-stateless does not force you to use a specific database or you
can work without database with stateless token.

It currently supports these storage backends out-of-the-box:

- MongoDB
- MySQL
- Redis
- Memcached
- Dynamodb
  
However, you are not not bound to these implementations.
By adhering to the interface defined by the base classes in ``oauth2.store``,
you can easily add an implementation of your backend.
It also is possible to mix different backends and e.g. read data of a client
from MongoDB while saving all tokens in memcached for fast access.

Take a look at the examples in the *examples* directory of the project.


Site adapter
************

- tornado
- flask
- uwsgi
  
Like for storage, oauth2-stateless does not define how you identify a
user or show a confirmation dialogue.
Instead your application should use the API defined by ``oauth2.web.SiteAdapter``.
