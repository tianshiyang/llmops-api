#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 4.8.25 PM9:55
@Author  : tianshiyang
@File    : jwt_service.py
"""
import os
from typing import Any

import jwt
from injector import inject
from dataclasses import dataclass

from internal.exception import UnauthorizedException


@inject
@dataclass
class JwtService:
    """jwt服务"""

    @classmethod
    def generate_token(cls, payload: dict[str, Any]) -> str:
        """根据传递的再喝信息生成token信息"""
        secret_key = os.getenv("JWT_SECRET_KEY")
        return jwt.encode(payload, secret_key, algorithm="HS256")

    @classmethod
    def parse_token(cls, token: str) -> dict[str, Any]:
        """解析传入的token信息得到载荷"""
        secret_key = os.getenv("JWT_SECRET_KEY")
        try:
            return jwt.decode(token, secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("授权认证凭证过期请重新登录")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("解析token出错，请重新登录")
        except Exception as e:
            raise UnauthorizedException(str(e))
