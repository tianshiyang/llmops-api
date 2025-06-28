#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 27.6.25 PM11:09
@Author  : tianshiyang
@File    : upload_file_handler.py
"""
from dataclasses import dataclass

from injector import inject

from internal.schema.upload_file_schema import UploadFileReq, UploadFileResp
from internal.service.cos_service import CosService
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class UploadFileHandler:
    cos_service: CosService

    def upload_file(self):
        req = UploadFileReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务上传文件并获取记录
        upload_file = self.cos_service.upload_file(req.file.data)

        # 构建返回结果
        reps = UploadFileResp()
        return success_json(reps.dump(upload_file))
