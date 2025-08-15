#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.8.25 PM5:05
@Author  : tianshiyang
@File    : api_key_service.py
"""
import secrets

from injector import inject
from dataclasses import dataclass

from internal.model import ApiKey, Account
from internal.schema.api_key_schema import CreateApiKeyReq
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class ApiKeyService(BaseService):
    """API秘钥服务"""
    db: SQLAlchemy

    def create_api_key(self, req: CreateApiKeyReq, account: Account) -> ApiKey:
        """根据传递的信息创建API秘钥"""
        return self.create(
            ApiKey,
            account_id=account.id,
            api_key=self.generate_api_key(),
            is_active=req.is_active.data,
            remark=req.remark.data,
        )

    @classmethod
    def generate_api_key(cls, api_key_prefix: str = "llmops-v1/") -> str:
        """生成一个长度为48的API秘钥，并携带前缀"""
        return api_key_prefix + secrets.token_urlsafe(48)
