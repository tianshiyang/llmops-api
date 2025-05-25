#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM6:54
@Author  : tianshiyang
@File    : 2.FileSystemBlobLoader示例.py
"""

from langchain_community.document_loaders.blob_loaders import FileSystemBlobLoader

loader = FileSystemBlobLoader(".", show_progress=True)

for blob in loader.yield_blobs():
    print(blob.as_string())
