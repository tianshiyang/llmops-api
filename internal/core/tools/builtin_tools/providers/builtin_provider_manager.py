#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 18.6.25 PM9:59
@Author  : tianshiyang
@File    : builtin_provider_manager.py
"""
import os.path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from internal.core.tools.builtin_tools.entities import Provider, ToolEntity
from internal.core.tools.builtin_tools.entities.provider_entity import ProviderEntity


class BuiltinProviderManager(BaseModel):
    """服务提供商工厂类"""
    provider_map: dict[str, Provider] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._get_provider_tool_map()

    def get_provider(self, provider_name: str) -> Provider:
        return self.provider_map[provider_name]

    def get_providers(self) -> list[Provider]:
        return list(self.provider_map.values())

    def get_provider_entities(self) -> list[ProviderEntity]:
        return [provider.provider_entity for provider in self.provider_map.values()]

    def get_tool(self, provider_name: str, tool_name: str) -> Any:
        provider = self.provider_map[provider_name]
        if provider is None:
            return None
        return provider.get_tool(tool_name)

    def _get_provider_tool_map(self):
        """项目初始化的时候获取服务提供商、工具的映射关系并填充provider_tool_map"""
        if self.provider_map:
            return
        current_path = os.path.abspath(__file__)
        provider_path = os.path.dirname(current_path)
        provider_yaml_path = os.path.join(provider_path, "provider.yaml")

        with open(provider_yaml_path, encoding="utf-8") as f:
            provider_yaml_data = yaml.safe_load(f)

        for idx, provider_data in enumerate(provider_yaml_data):
            provider_entity = ProviderEntity(**provider_data)
            self.provider_map[provider_data.name] = Provider(
                name=provider_entity.name,
                position=idx,
                provider_entity=provider_entity
            )
