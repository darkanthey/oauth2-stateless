# -*- coding: utf-8 -*-

from oauth2.datatype import AccessToken
from oauth2.error import AccessTokenNotFound
from oauth2.store import AccessTokenStore
from oauth2.tokengenerator import StatelessTokenGenerator


class TokenStore(AccessTokenStore):
    """Uses stateless token to validate access tokens and auth tokens.

    This Dummy store for supports ``stateless``. Arguments are passed to the underlying client implementation.

    Initialization::

        from oauth2.store.stateless import TokenStore
        from oauth2.tokengenerator import StatelessTokenGenerator

        stateless_token = StatelessTokenGenerator(secret_key='xxx')
        token_store = TokenStore(stateless_token)
    """

    def __init__(self, stateless_token):
        if isinstance(stateless_token, StatelessTokenGenerator) is False:
            raise AccessTokenNotFound(
                "Token store adapter must inherit from class '{0}'".format(self.site_adapter_class.__name__)
            )
        self.stateless_token = stateless_token

    def save_token(self, access_token):
        """
        Just dummy interface who imulate store tokens.
        See :class:`oauth2.store.AccessTokenStore`.
        """
        pass

    def delete_refresh_token(self, refresh_token):
        """
        Just dummy interface who imulate delete tokens.

        :param refresh_token: The refresh token to delete.
        """
        pass

    def fetch_by_refresh_token(self, refresh_token):
        """
        Stateless token can generate oauth new tokens by refresh token.
        """
        data = self.stateless_token.validate_token(token, 'refresh_token')
        return datatype.AccessToken(**data)

    def fetch_existing_token_of_user(self, client_id, grant_type, user_id):
        """
        Stateless implementation can't fitch token.
        """
        pass
