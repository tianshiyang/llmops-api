#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 4.8.25 PM10:46
@Author  : tianshiyang
@File    : account_service.py
"""
from uuid import UUID

from injector import inject
from dataclasses import dataclass

from internal.model import Account
from internal.service import JwtService
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AccountService(BaseService):
    """账号服务"""
    db: SQLAlchemy
    jwt_service: JwtService

    def get_account(self, account_id: UUID) -> Account:
        """根据id获取指定的账号类型"""
        return self.get(Account, account_id)
