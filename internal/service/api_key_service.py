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

from sqlalchemy import desc

from internal.model import ApiKey, Account
from internal.schema.api_key_schema import CreateApiKeyReq
from internal.service.base_service import BaseService
from pkg.paginator.paginator import PaginatorReq, Paginator
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

    def get_api_keys_with_page(self, req: PaginatorReq, account: Account) -> tuple[list[ApiKey], Paginator]:
        """根据传递的信息获取API秘钥分页列表数据"""
        # 1.构建分页器
        paginate = Paginator(db=self.db, req=req)

        # 2.执行分页并获取数据
        api_keys = paginate.paginate(
            self.db.session.query(ApiKey).filter(
                ApiKey.account_id == account.id
            ).order_by(desc("created_at"))
        )

        return api_keys, paginate

    @classmethod
    def generate_api_key(cls, api_key_prefix: str = "llmops-v1/") -> str:
        """生成一个长度为48的API秘钥，并携带前缀"""
        return api_key_prefix + secrets.token_urlsafe(48)
