"""
Ensures compatibility between python 2.x and python 3.x
and The availability of which depends on the developer's preferences.
"""

import sys

if sys.version_info >= (3, 0):
    from urllib.parse import parse_qs  # pragma: no cover
    from urllib.parse import urlencode  # pragma: no cover
    from urllib.parse import quote  # pragma: no cover
else:
    from urlparse import parse_qs  # pragma: no cover
    from urllib import urlencode  # pragma: no cover
    from urllib import quote  # pragma: no cover

try:
    import ujson as json  # pragma: no cover
except ImportError:
    import json  # pragma: no cover
