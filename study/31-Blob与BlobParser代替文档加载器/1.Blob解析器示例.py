#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM6:54
@Author  : tianshiyang
@File    : 1.Blob解析器示例.py
"""
from typing import Iterator

from langchain_core.document_loaders import BaseBlobParser
from langchain_core.documents import Document
from langchain_core.documents.base import Blob


class CustomParser(BaseBlobParser):
    def __init__(self, blob: Blob):
        self.blob = blob

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        with blob.as_bytes_io() as f:
            line_number = 0
            for line in f:
                yield Document(
                    page_content=line,
                    metadata={"source": blob.source, "line_number": line_number}
                )
                line_number += 1


blob = Blob.from_path("./喵喵.txt")
parser = CustomParser(blob)

# 2.解析得到文档数据
documents = list(parser.lazy_parse(blob))

# 3.输出相应的信息
print(documents)
print(len(documents))
print(documents[0].metadata)
