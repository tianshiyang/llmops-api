#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.6.25 PM11:55
@Author  : tianshiyang
@File    : builtin_tool_service.py
"""
from typing import Any

from injector import inject
from dataclasses import dataclass

from internal.core.tools.builtin_tools.categories import BuiltinCategoryManager


@inject
@dataclass
class BuiltinToolService:
    builtin_category_manager: BuiltinCategoryManager

    def get_categories(self) -> list[dict[str, Any]]:
        """获取所有的内置分类信息，涵盖了category、name、icon"""
        category_map = self.builtin_category_manager.get_category_map()
        return [{
            "name": category["entity"].name,
            "category": category["entity"].category,
            "icon": category["icon"],
        } for category in category_map.values()]
