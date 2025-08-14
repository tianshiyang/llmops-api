#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 14.8.25 PM6:01
@Author  : tianshiyang
@File    : api_provider_manager.py
"""
from dataclasses import dataclass
from injector import inject
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from internal.core.tools.api_tools.entities.tool_entity import ToolEntity


@inject
@dataclass
class ApiProviderManager(BaseModel):

    def get_tool(self, tool_entity: ToolEntity) -> BaseTool:
        pass
