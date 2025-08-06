#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 6.8.25 PM8:04
@Author  : tianshiyang
@File    : __init__.py.py
"""
from .oauth import OAuthUserInfo, OAuth
from .github_oauth import GitHubOAuth

__all__ = ["OAuthUserInfo", "OAuth", "GitHubOAuth"]
