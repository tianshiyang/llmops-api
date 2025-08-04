#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 27.6.25 PM11:09
@Author  : tianshiyang
@File    : upload_file_handler.py
"""
from dataclasses import dataclass

from flask_login import login_required, current_user
from injector import inject

from internal.schema.upload_file_schema import UploadFileReq, UploadFileResp, UploadImageReq
from internal.service.cos_service import CosService
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class UploadFileHandler:
    cos_service: CosService

    @login_required
    def upload_file(self):
        req = UploadFileReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务上传文件并获取记录
        upload_file = self.cos_service.upload_file(req.file.data, current_user)

        # 构建返回结果
        reps = UploadFileResp()
        return success_json(reps.dump(upload_file))

    @login_required
    def upload_image(self):
        req = UploadImageReq()
        if not req.validate():
            return validate_error_json(req.errors)

        upload_file = self.cos_service.upload_file(req.file.data, only_image=True, account=current_user)

        image_url = self.cos_service.get_file_url(upload_file.key)
        return {
            "image_url": image_url
        }
