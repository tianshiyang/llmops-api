#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 7.8.25 AM12:02
@Author  : tianshiyang
@File    : oauth_handler.py
"""
from injector import inject
from dataclasses import dataclass

from internal.service import OAuthService
from pkg.response import success_json


@inject
@dataclass
class OAuthHandler:
    oauth_service: OAuthService
    """第三方授权认证处理器"""

    def provider(self, provider_name: str):
        """根据传递的服务商名字获取授权认证重定向地址"""
        # 1.根据provider_name获取授权服务提供商
        oauth = self.oauth_service.get_oauth_by_provider_name(provider_name)

        # 2.调用函数获取授权地址
        redirect_uri = oauth.get_authorization_url()

        return success_json({"redirect_uri": redirect_uri})
