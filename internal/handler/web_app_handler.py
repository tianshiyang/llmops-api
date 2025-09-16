#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.9.25 PM9:51
@Author  : tianshiyang
@File    : web_app_handler.py
"""
from flask_login import login_required
from injector import inject
from dataclasses import dataclass

from internal.schema.web_app_schema import GetWebAppResp
from internal.service import WebAppService
from pkg.response import success_json


@inject
@dataclass
class WebAppHandler:
    web_app_service: WebAppService

    @login_required
    def get_web_app(self, token: str):
        """根据传递的token凭证标识获取WebApp基础信息"""
        # 1.调用服务根据传递的token获取应用信息
        app = self.web_app_service.get_web_app(token)

        # 2.构建响应结构并返回
        resp = GetWebAppResp()
        return success_json(resp.dump(app))
