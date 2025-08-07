#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 8.8.25 AM12:36
@Author  : tianshiyang
@File    : auth_handler.py
"""
from flask_login import login_required, logout_user
from injector import inject
from dataclasses import dataclass

from internal.schema.auth_schema import PasswordLoginReq, PasswordLoginResp
from internal.service import AccountService
from pkg.response import validate_error_json, success_json, success_message


@inject
@dataclass
class AuthHandler:
    """LLMOps平台自有授权认证处理器"""
    account_service: AccountService

    def password_login(self):
        """账号密码登录"""
        # 1.提取请求并验证数据
        req = PasswordLoginReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用登录服务登录账号
        credential = self.account_service.password_login(req.email.data, req.password.data)

        # 3. 创建响应结构并返回
        resp = PasswordLoginResp()
        return success_json(resp.dumps(credential))

    @login_required
    def logout(self):
        """退出登录，用于提示前端清除授权凭证"""
        logout_user()
        return success_message("退出登录成功")
