"""
Ensures compatibility of libraries
and The availability of which depends on the developer's preferences.
"""

from urllib.parse import parse_qs  # pragma: no cover
from urllib.parse import urlencode  # pragma: no cover
from urllib.parse import quote  # pragma: no cover

try:
    import ujson as json  # pragma: no cover
except ImportError:
    import json  # pragma: no cover
