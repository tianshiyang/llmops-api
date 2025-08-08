#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 8.8.25 AM11:23
@Author  : tianshiyang
@File    : account_handler.py
"""
from flask_login import login_required, current_user
from injector import inject
from dataclasses import dataclass

from internal.schema.account_schema import GetCurrentUserResp
from internal.service import AccountService
from pkg.response import success_json


@inject
@dataclass
class AccountHandler:
    """账号设置处理器"""
    account_service: AccountService

    @login_required
    def get_current_user(self):
        """获取当前登录账号信息"""
        resp = GetCurrentUserResp()
        return success_json(resp.dump(current_user))
