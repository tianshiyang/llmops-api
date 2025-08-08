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

from internal.schema.account_schema import GetCurrentUserResp, UpdatePasswordReq
from internal.service import AccountService
from pkg.response import success_json, validate_error_json, success_message


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

    @login_required
    def update_password(self):
        """更新当前登录账号密码"""
        # 1. 提取请求数据并校验
        req = UpdatePasswordReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务更新账号密码
        self.account_service.update_password(req.password.data, current_user)
        return success_message("更新账号密码成功")
