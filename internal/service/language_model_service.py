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
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class LanguageModelService(BaseService):
    db: SQLAlchemy

    def get_language_models(self) -> list[dict[str, Any]]:
        pass

    def get_language_model(self, provider_name: str, model_name: str):
        pass

    def get_language_model_icon(self, provider_name: str):
        pass
