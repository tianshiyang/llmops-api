#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 1.7.25 PM7:08
@Author  : tianshiyang
@File    : file_extractor.py
"""
import os.path
import tempfile
from pathlib import Path
from typing import Union

import requests
from injector import inject
from dataclasses import dataclass

from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredPDFLoader, \
    UnstructuredMarkdownLoader, UnstructuredHTMLLoader, UnstructuredCSVLoader, UnstructuredXMLLoader, \
    UnstructuredPowerPointLoader, UnstructuredFileLoader, TextLoader

from internal.model.upload_file import UploadFile
from internal.service.cos_service import CosService
from langchain_core.documents import Document as LCDocument


@inject
@dataclass
class FileExtractor:
    """文件提取提，用于将远程文件、upload_file记录加载成LangChain对应的文档或字符串"""
    cos_service: CosService

    def load(self, upload_file: UploadFile, return_text: bool = False, is_unstructured: bool = True) -> Union[
        list[LCDocument], str]:
        # 1.创建一个临时的文件夹
        with tempfile.TemporaryDirectory() as temp_dir:
            # 2.构建一个临时文件路径
            file_path = os.path.join(temp_dir, os.path.basename(upload_file.key))
            # 3.将对象存储中的文件下载到本地
            self.cos_service.download_file(upload_file.key, file_path)
            # 4.从指定的路径中加载文件
            return self.load_from_file(file_path, return_text, is_unstructured=is_unstructured)

    @classmethod
    def load_from_url(cls, url: str, return_text: bool = False):
        response = requests.get(url)
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, os.path.basename(url))
            with open(file_path, "wb") as f:
                f.write(response.content)
            return cls.load_from_file(file_path, return_text)

    @classmethod
    def load_from_file(cls, file_path: str, return_text: bool = False, is_unstructured: bool = True) -> Union[
        list[LCDocument], str]:
        """从本地文件中加载数据，返回LangChain文档列表或者字符串"""
        # 获取文件扩展名
        delimiter = "\n\n"
        file_extension = Path(file_path).suffix.lower()

        # 根据不同的文件加载不同的加载器
        if file_extension in [".xlsx", ".xls"]:
            loader = UnstructuredExcelLoader(file_path)
        elif file_extension == ".pdf":
            loader = UnstructuredPDFLoader(file_path)
        elif file_extension in [".md", ".markdown"]:
            loader = UnstructuredMarkdownLoader(file_path)
        elif file_extension in ["htm", "html"]:
            loader = UnstructuredHTMLLoader(file_path)
        elif file_extension == ".csv":
            loader = UnstructuredCSVLoader(file_path)
        elif file_extension == ".xml":
            loader = UnstructuredXMLLoader(file_path)
        elif file_extension in [".ppt", ".pptx"]:
            loader = UnstructuredPowerPointLoader(file_path)
        else:
            loader = UnstructuredFileLoader(file_path) if is_unstructured else TextLoader(file_path)
        # 3.返回加载的文档列表或文本
        return delimiter.join([document.page_content for document in loader.load()] if return_text else loader.load())
