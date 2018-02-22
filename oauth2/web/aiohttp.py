#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. warning::
   aiohttp support is currently experimental.

Use aiohttp to serve token requests:

.. literalinclude:: examples/aiohttp_server.py
"""

from __future__ import absolute_import

from aiohttp import web


class Request(object):
    """Contains data of the current HTTP request."""

    def __init__(self, request, data=None):
        self.request = request
        self.data = data

    @property
    def method(self):
        return self.request.method

    @property
    def path(self):
        return self.request.path

    @property
    def query_string(self):
        return self.request.query_string

    def get_param(self, name, default=None):
        return self.request.query.get(name, default)

    def post_param(self, name, default=None):
        return self.data.get(name, default)

    def header(self, name, default=None):
        return self.request.headers.get(name, default)


class OAuth2Handler:
    def __init__(self, provider):
        """
        :type provider: :class:`oauth2.Provider`
        """
        self.provider = provider

    async def dispatch_request(self, request):
        response = self.provider.dispatch(request=Request(request), environ=dict())
        return self._map_response(response)

    async def post_dispatch_request(self, request):
        data = await request.post()
        response = self.provider.dispatch(request=Request(request, data), environ=dict())
        return self._map_response(response)

    def _map_response(self, response):
        return web.Response(body=response.body, status=response.status_code, headers=response.headers)
