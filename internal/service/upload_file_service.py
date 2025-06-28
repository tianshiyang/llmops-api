#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM2:58
@Author  : tianshiyang
@File    : upload_file_service.py
"""
from internal.model.upload_file import UploadFile
from internal.service.base_service import BaseService
from dataclasses import dataclass
from injector import inject

from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class UploadFileService(BaseService):
    db: SQLAlchemy

    def create_upload_file(self, **kwargs) -> UploadFile:
        return self.create(UploadFile, **kwargs)
