#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 12.9.25 PM1:55
@Author  : tianshiyang
@File    : language_model_service.py
"""
from dataclasses import dataclass
from typing import Any

from injector import inject

from internal.core.language_model.language_model_manager import LanguageModelManager
from internal.lib.helper import convert_model_to_dict
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class LanguageModelService(BaseService):
    db: SQLAlchemy
    language_model_manager: LanguageModelManager

    def get_language_models(self) -> list[dict[str, Any]]:
        """获取LLMOps项目中的所有模型列表信息"""
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
        pass

    def get_language_model_icon(self, provider_name: str):
        pass
