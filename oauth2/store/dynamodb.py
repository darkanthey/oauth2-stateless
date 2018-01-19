# -*- coding: utf-8 -*-

from oauth2.datatype import AccessToken
from oauth2.error import AccessTokenNotFound
from oauth2.store import AccessTokenStore


class DynamodbStore(object):
    """
    Uses dynamodb to store access tokens and auth tokens.

    This Store supports ``dynamodb``. Arguments are passed to the
    underlying client implementation. For connect to dynamodb use python boto library.
    http://boto.cloudhackers.com/en/latest/dynamodb_tut.html

    Initialization::

        from oauth2.store.dynamodb import TokenStore
        # oauth_token = Table('oauth_access_token')
        oauth_token = Table.create('users',
                                   schema=[HashKey('token_key')],
                                   global_indexes=[
                                     GlobalAllIndex('RefreshToken-index', parts=[HashKey('refresh_token')])
                                   ])

        token_store = TokenStore(oauth_token)
    """
    def __init__(self, connect):
        self.connect = connect


class TokenStore(AccessTokenStore, DynamodbStore):
    """Dynamodb Access Token Store"""

    def save_token(self, access_token):
        """
        Stores the access token and additional data in redis.
        See :class:`oauth2.store.AccessTokenStore`.
        """
        unique_token_key = self._unique_token_key(access_token.client_id, access_token.grant_type, access_token.user_id)

        storing_unique_token = access_token.__dict__
        storing_unique_token.update({'token_key': unique_token_key})
        self.connect.put_item(**storing_unique_token)

    def delete_refresh_token(self, refresh_token):
        """
        Deletes a refresh token after use

        :param refresh_token: The refresh token to delete.
        """
        access_token = self.fetch_by_refresh_token(refresh_token)
        self.connect.delete({'token_key': access_token.token})

    def fetch_by_refresh_token(self, refresh_token):
        """
        Find oauth tokens by refresh token.
        """
        tokens_data = self.connect.query2(refresh_token__eq=refresh_token,
                                          index='RefreshToken-index', limit=1)
        tokens_res = list(tokens_data)
        if not tokens_res:
            raise error.AccessTokenNotFound
        token_data = tokens_res.pop()
        if token_data is None:
            raise error.AccessTokenNotFound
        data = token_data._data.get('token')  # pylint: disable=protected-access
        del data['token_key']
        return datatype.AccessToken(**data)

    def fetch_existing_token_of_user(self, client_id, grant_type, user_id):
        """
        Find oauth access token by client_id, grant_type, user_id.
        """
        unique_token_key = self._unique_token_key(client_id=client_id, grant_type=grant_type, user_id=user_id)
        token_data = self.connect.get_item(token_key=unique_token_key)
        if token_data is None:
            raise error.AccessTokenNotFound
        return datatype.AccessToken(**token_data)

    @classmethod
    def _unique_token_key(cls, client_id, grant_type, user_id):
        return "{0}_{1}_{2}".format(client_id, grant_type, user_id)
