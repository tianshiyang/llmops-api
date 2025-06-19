#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.6.25 PM11:55
@Author  : tianshiyang
@File    : builtin_tool_service.py
"""
import mimetypes
import os.path
from typing import Any

from flask import current_app
from injector import inject
from dataclasses import dataclass

from pydantic import BaseModel

from internal.core.tools.builtin_tools.categories import BuiltinCategoryManager
from internal.core.tools.builtin_tools.providers.builtin_provider_manager import BuiltinProviderManager
from internal.exception import NotFoundException


@inject
@dataclass
class BuiltinToolService:
    builtin_category_manager: BuiltinCategoryManager
    builtin_provider_manager: BuiltinProviderManager

    def get_categories(self) -> list[dict[str, Any]]:
        """获取所有的内置分类信息，涵盖了category、name、icon"""
        category_map = self.builtin_category_manager.get_category_map()
        return [{
            "name": category["entity"].name,
            "category": category["entity"].category,
            "icon": category["icon"],
        } for category in category_map.values()]

    def get_builtin_tools(self) -> list[dict[str, Any]]:
        """获取LLMOps项目中的所有内置提供商+工具对应的信息"""
        providers = self.builtin_provider_manager.get_providers()
        builtin_tools = []
        for provider in providers:
            provider_entity = provider.provider_entity
            builtin_tool = {
                **provider_entity.model_dump(exclude=set("icon")),
                "tools": [],
            }

            # 3.循环遍历提取提供者的所有工具实体
            for tool_entity in provider.get_tool_entities():
                # 4.从提供者中获取工具函数
                tool = provider.get_tool(tool_entity.name)
                # 5.构建工具实体信息
                tool_dict = {
                    **tool_entity.model_dump(),
                    "inputs": self.get_tool_inputs(tool),
                }
                builtin_tool["tools"].append(tool_dict)
            builtin_tools.append(builtin_tool)

        return builtin_tools

    def get_get_provider_icon(self, provider_name: str) -> Any:
        """根据传递的提供者名字获取icon流信息"""
        provider = self.builtin_provider_manager.get_provider(provider_name)
        if not provider:
            raise NotFoundException(f"该工具提供者{provider_name}不存在")
        # 获取项目根目录信息
        root_path = os.path.dirname(os.path.dirname(current_app.root_path))

        # 3.拼接得到提供者所在的文件夹
        provider_path = os.path.join(
            root_path,
            "internal", "core", "tools", "builtin_tools", "providers", provider_name,
        )

        # 4.拼接得到icon对应的路径
        icon_path = os.path.join(provider_path, "_asset", provider.provider_entity.icon)

        # 5.检测icon是否存在
        if not os.path.exists(icon_path):
            raise NotFoundException(f"该工具提供者_asset下未提供图标")

        # 6.读取icon的类型
        mimetype, _ = mimetypes.guess_type(icon_path)
        mimetype = mimetype or "application/octet-stream"

        # 7.读取icon的字节数据
        with open(icon_path, "rb") as f:
            byte_data = f.read()
            return byte_data, mimetype
        return provider

    @classmethod
    def get_tool_inputs(cls, tool) -> list:
        """根据传入的工具获取inputs信息"""
        inputs = []

        if hasattr(tool, "args_schema") and issubclass(tool.args_schema, BaseModel):
            for field_name, model_field in tool.args_schema.__pydantic_fields__.items():
                inputs.append({
                    "name": field_name,
                    "description": model_field.description,
                    "required": model_field.is_required(),
                    "type": model_field.description,
                })
        return inputs
