#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 7.8.25 AM12:04
@Author  : tianshiyang
@File    : oauth_service.py
"""
import os

from injector import inject
from dataclasses import dataclass

from internal.exception import NotFoundException
from internal.service import JwtService
from internal.service.base_service import BaseService
from pkg.oauth import OAuth, GitHubOAuth
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class OAuthService(BaseService):
    """根据传递的服务提供商名字获取授权服务"""
    db: SQLAlchemy
    jwt_service: JwtService

    # account_service: AccountService

    @classmethod
    def get_all_oauth(cls) -> dict[str, OAuth]:
        """获取LLMOps集成的所有第三方授权方式"""
        # 1.实例化集成的第三方授权认证OAuth
        github = GitHubOAuth(
            client_id=os.getenv("GITHUB_CLIENT_ID"),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
            redirect_uri=os.getenv("GITHUB_REDIRECT_URI")
        )

        # 2.构建字典并返回
        return {
            "github": github,
        }

    @classmethod
    def get_oauth_by_provider_name(cls, provider_name: str) -> OAuth:
        """根据传递的服务提供商名字获取授权服务"""
        all_oauth = cls.get_all_oauth()
        oauth = all_oauth.get(provider_name)

        if oauth is None:
            raise NotFoundException(f"该授权方式[{provider_name}]不存在")
        return oauth
