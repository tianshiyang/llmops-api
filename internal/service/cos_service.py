#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 AM11:21
@Author  : tianshiyang
@File    : cos_service.py
"""
import hashlib
import os
import uuid
from datetime import datetime

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from werkzeug.datastructures import FileStorage

from internal.entity.upload_file_entity import ALLOWED_IMAGE_EXTENSION, ALLOWED_DOCUMENT_EXTENSION
from internal.exception import FailException
from internal.model import Account
from internal.model.upload_file import UploadFile
from internal.service.upload_file_service import UploadFileService
from dataclasses import dataclass

from injector import inject


@inject
@dataclass
class CosService:
    """腾讯云cos对象存储服务"""
    upload_file_service: UploadFileService

    def upload_file(self, file: FileStorage, only_image: bool = False, account: Account = None) -> UploadFile:
        """上传文件到腾讯云cos对象存储，上传后返回文件的信息"""
        # 获取文件名称
        filename = file.filename
        extension = file.filename.rsplit(".", maxsplit=1)[-1] if "." in filename else ""
        if extension.lower() not in (ALLOWED_IMAGE_EXTENSION + ALLOWED_DOCUMENT_EXTENSION):
            raise FailException(f"该.{extension}扩展的文件不允许上传")
        elif only_image and extension not in ALLOWED_IMAGE_EXTENSION:
            raise FailException(f"该.{extension}扩展的文件不支持上传，请上传正确的图片")

        # 2.获取客户端+存储桶名字
        client = self._get_client()
        bucket = self._get_bucket()

        # 生成一个随机的名字
        random_filename = str(uuid.uuid4()) + f".{extension}"
        now = datetime.now()
        upload_filename = f"{now.year}/{now.month:02d}/{now.day:02d}/{random_filename}"

        # 4.流式读取上传的数据并将其上传到cos中
        file_content = file.stream.read()

        try:
            client.put_object(
                Bucket=bucket,
                Key=upload_filename,
                Body=file_content,
            )
        except Exception as e:
            raise FailException("上传文件失败，请稍后重试")

        return self.upload_file_service.create_upload_file(
            account_id=account.id,
            name=filename,
            key=upload_filename,
            size=len(file_content),
            extension=extension,
            mime_type=file.mimetype,
            hash=hashlib.sha3_256(file_content).hexdigest(),
        )

    def get_file_url(self, key: str) -> str:
        cos_domain = os.getenv("COS_DOMAIN")
        if not cos_domain:
            bucket = os.getenv("COS_BUCKET")
            scheme = os.getenv("COS_SCHEME")
            region = os.getenv("COS_REGION")
            cos_domain = f"{scheme}://{bucket}.cos.{region}.myqcloud.com"
        return f"{cos_domain}/{key}"

    def download_file(self, key: str, target_file_path: str):
        # 下载文件
        client = self._get_client()
        bucket = self._get_bucket()
        client.download_file(bucket, key, target_file_path)

    @classmethod
    def _get_client(cls):
        region = os.getenv("COS_REGION")
        secret_id = os.getenv("COS_SECRET_ID")
        secret_key = os.getenv("COS_SECRET_KEY")
        scheme = os.getenv("COS_SCHEME")
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Scheme=scheme)
        return CosS3Client(config)

    @classmethod
    def _get_bucket(cls):
        return os.getenv("COS_BUCKET")
