#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classes for handling flask HTTP request/response flow.
"""

from functools import wraps
from typing import Dict, Optional

from flask import request


class Request(object):
    """Contains data of the current HTTP request."""

    def __init__(self, request: request) -> None:
        self.request = request

    @property
    def method(self) -> str:
        return self.request.method

    @property
    def path(self) -> str:
        return self.request.path

    @property
    def query_string(self) -> Dict[str, str]:
        return self.request.query_string

    def get_param(self, name: str, default: Optional[str]=None) -> Optional[str]:
        return self.request.args.get(name, default)

    def post_param(self, name: str, default: Optional[str]=None) -> Optional[str]:
        return self.request.form.get(name, default)

    def header(self, name: str, default: Optional[str]=None) -> Optional[str]:
        return self.request.headers.get(name, default)


def oauth_request_hook(oauth2_server):
    """Initialise Oauth2 interface bewtween flask and oauth2 server"""

    def wrapper(fn):
        @wraps(fn)
        def decorated_fn(*args, **kwargs):
            # We are not call fn(args, kwargs) because oauth.dispatch should doing that.
            response = oauth2_server.provider.dispatch(Request(request), request.environ)
            return (response.body, response.status_code, response.headers.items())
        return decorated_fn
    return wrapper
