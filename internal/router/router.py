#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.4.25 PM11:38
@Author  : 1685821150@qq.com
@File    : router.py
"""
from dataclasses import dataclass

from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler, BuiltinToolHandler


@inject
@dataclass
class Router:
    """"路由"""

    app_handler: AppHandler

    builtin_tool_handler: BuiltinToolHandler

    def register_router(self, app: Flask):
        """注册路由"""
        # 1. 创建一个蓝图（一组路由的集合）
        bp = Blueprint('llmops', __name__, url_prefix='')

        # 2.将url与对应的控制器方法做绑定
        bp.add_url_rule('/apps/<uuid:app_id>/debug', view_func=self.app_handler.debug, methods=['POST'])
        bp.add_url_rule('/ping', view_func=self.app_handler.ping)
        bp.add_url_rule('/app/completion', methods=["POST"], view_func=self.app_handler.completion)
        bp.add_url_rule('/app', methods=["POST"], view_func=self.app_handler.create_app)
        bp.add_url_rule('/app/<uuid:id>', view_func=self.app_handler.get_app)
        bp.add_url_rule('/app/<uuid:id>', methods=["POST"], view_func=self.app_handler.update_app)
        bp.add_url_rule('/app/<uuid:id>/delete', methods=["POST"], view_func=self.app_handler.delete_app)

        # 3.内置插件广场模块
        bp.add_url_rule("/builtin-tools", view_func=self.builtin_tool_handler.get_builtin_tools)
        # 3.1获取插件广场所有分类信息（不分页）
        bp.add_url_rule("/builtin-tools/categories", view_func=self.builtin_tool_handler.get_categories)
        # 6. 在应用上注册蓝图
        app.register_blueprint(bp)
