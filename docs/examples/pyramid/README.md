Pyramid integration example for oauth2-stateless

Integrate the example:

1. Put classes in base.py in appropriate packages. 
2. impl.py contains controller and site adapter. Also place both of them in appropriate packages. 
3. Implement "password_auth" method in OAuth2SiteAdapter.
4. Modify "_get_token_store" and "_get_client_store" methods in UserAuthController
5. Add "config.add_route('authenticateUser', '/user/token')"  to "\__init__\.py"
