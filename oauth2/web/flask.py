#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classes for handling flask HTTP request/response flow.
"""

from __future__ import absolute_import

from functools import wraps

from flask import request


class Request(object):
    """Contains data of the current HTTP request."""

    def __init__(self, request):
        self.request = request

    @property
    def method(self):
        return self.request.method

    @property
    def path(self):
        return self.request.path

    @property
    def query_string(self):
        return self.request.query_string.decode('utf-8')

    def get_param(self, name, default=None):
        return self.request.args.get(name, default)

    def post_param(self, name, default=None):
        if self.header('Content-Type') == 'application/json':
            return self.request.json.get(name, default)
        return self.request.form.get(name, default)

    def header(self, name, default=None):
        return self.request.headers.get(name, default)


def oauth_request_hook(provider):
    """Initialise Oauth2 interface bewtween flask and oauth2 server"""

    def wrapper(fn):
        @wraps(fn)
        def decorated_fn(*args, **kwargs):
            # We are not call fn(args, kwargs) because oauth.dispatch should doing that.
            response = provider.dispatch(Request(request), request.environ)
            return response.body, response.status_code, response.headers.items()
        return decorated_fn
    return wrapper
