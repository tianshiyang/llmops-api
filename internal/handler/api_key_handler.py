#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.8.25 PM2:51
@Author  : tianshiyang
@File    : api_key_handler.py
"""
from dataclasses import dataclass

from flask_login import login_required, current_user
from injector import inject

from internal.schema.api_key_schema import CreateApiKeyReq
from internal.service.api_key_service import ApiKeyService
from pkg.response import validate_error_json, success_message


@inject
@dataclass
class ApiKeyHandler:
    """API秘钥处理器"""
    api_key_service: ApiKeyService

    @login_required
    def create_api_key(self):
        """创建API秘钥"""
        # 1.提取请求并校验
        req = CreateApiKeyReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务创建秘钥
        self.api_key_service.create_api_key(req, current_user)
        return success_message("创建API秘钥成功")
