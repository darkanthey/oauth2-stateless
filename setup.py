import os

from setuptools import setup

setup(name="oauth2-stateless",
      version='1.1.0',
      description="OAuth 2.0 provider for python with Stateless tokens support",
      long_description=open("README.md").read(),
      author="Andrew Grytsenko",
      author_email="darkanthey@gmail.com",
      url="https://github.com/darkanthey/oauth2-stateless",
      packages=[d[0].replace("/", ".") for d in os.walk("oauth2") if not d[0].endswith("__pycache__")],
      install_requires=[
          "ujson",
          "itsdangerous"
      ],
      extras_require={
          "memcache": ["python-memcached"],
          "mongodb": ["pymongo"],
          "redis": ["redis"]
      },
      classifiers=[
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6"
      ]
      )
