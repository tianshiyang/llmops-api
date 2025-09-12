#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 12.9.25 PM1:55
@Author  : tianshiyang
@File    : language_model_service.py
"""
import mimetypes
import os.path
from dataclasses import dataclass
from typing import Any

from flask import current_app
from injector import inject

from internal.core.language_model.language_model_manager import LanguageModelManager
from internal.exception import NotFoundException
from internal.lib.helper import convert_model_to_dict
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class LanguageModelService(BaseService):
    db: SQLAlchemy
    language_model_manager: LanguageModelManager

    def get_language_models(self) -> list[dict[str, Any]]:
        """获取LLMOps项目中的所有模型列表信息1"""
        # 1. 调用语言模型管理器获取提供商列表
        providers = self.language_model_manager.get_providers()

        # 2.构建语言模型列表，循环读取数据
        language_models = []
        for provider in providers:
            # 3.获取提供商实体和模型实体列表
            provider_entity = provider.provider_entity
            model_entities = provider.get_model_entities()

            # 4.构建响应字典结构
            language_model = {
                "name": provider_entity.name,
                "position": provider.position,
                "label": provider_entity.label,
                "icon": provider_entity.icon,
                "description": provider_entity.description,
                "background": provider_entity.background,
                "support_model_types": provider_entity.supported_model_types,
                "models": convert_model_to_dict(model_entities),
            }
            language_models.append(language_model)

        return language_models

    def get_language_model(self, provider_name: str, model_name: str):
        """根据传递的提供者名字+模型名字获取模型详细信息"""
        # 1. 获取提供者+模型名字实体
        provider = self.language_model_manager.get_provider(provider_name)
        if not provider:
            raise NotFoundException("该服务提供者不存在")

        # 2.获取模型实体
        model_entity = provider.get_model_entity(model_name)
        if not model_entity:
            raise NotFoundException("该模型不存在")
        return convert_model_to_dict(model_entity)

    def get_language_model_icon(self, provider_name: str):
        """根据传递的提供者名字获取提供商对应的图标信息"""
        # 1.获取提供商信息
        provider = self.language_model_manager.get_provider(provider_name)
        if not provider:
            raise NotFoundException("该服务提供者不存在")

        # 2.获取项目的根路径信息
        root_path = os.path.dirname(os.path.dirname(current_app.root_path))

        # 3.拼接得到提供者所在的文件夹
        provider_path = os.path.join(
            root_path,
            "internal", "core", "language_model", "providers", provider_name,
        )

        # 4.拼接得到icon对应的路径
        icon_path = os.path.join(provider_path, "_asset", provider.provider_entity.icon)

        # 5.检测icon是否存在
        if not os.path.exists(icon_path):
            raise NotFoundException(f"该模型提供者_asset下未提供图标")

        # 6.读取icon的类型
        mimetype, _ = mimetypes.guess_type(icon_path)
        mimetype = mimetype or "application/octet-stream"

        # 7.读取icon的字节数据
        with open(icon_path, "rb") as f:
            byte_data = f.read()
            return byte_data, mimetype
