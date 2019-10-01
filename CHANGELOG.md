## 1.1.1

Features:

  - Remove PY2 support ([@darkanthey][])

Bugfixes:

  - Fix test DeprecationWarning: Please use assertRegex instead.
  - Add more example with user_id example.
  - Add requirements-dev.txt and all datastore and web adapter move there.

## 1.1.0

Features:

  - aiohttp web framework support ([@darkanthey][])

Bugfixes:

  - For wider support redis version rs.setex was replaced by rs.set with ex param.

## 1.0.3

Bugfixes:

  - All examples modified to support both PY3/PY2 versions. ([@darkanthey][])
  - flask_server example was added. ([@darkanthey][])
  - json throughout the project now imported from oauth2.compatibility. ([@darkanthey][])
  - Support aiohttp are coming. ([@darkanthey][])

## 1.0.2

Bugfixes:

  - Some oauth implementations have 'Content-Type: application/json' for oauth/token. ([@darkanthey][])

## 1.0.1

Bugfixes:

  - Fix an exception when requesting an unknown URL on Python 3.x ([@darkanthey][])
  - Add error message to response for bad redirect URIs. ([@darkanthey][])

## 1.0.0

Features:

  - Stateless token support ([@darkanthey][])
  - Dynamodb token store ([@darkanthey][])
  - Support for Python 2.7 - 3.7 ([@darkanthey][])

[@darkanthey]: https://github.com/darkanthey
