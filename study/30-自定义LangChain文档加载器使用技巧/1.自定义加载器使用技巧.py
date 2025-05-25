#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM6:53
@Author  : tianshiyang
@File    : 1.自定义加载器使用技巧.py
"""
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class CustomDocumentLoader(BaseLoader):
    def __init__(self, path):
        self.path = path

    def lazy_load(self):
        with open(self.path, encoding="utf-8") as f:
            line_number = 0
            for line in f:
                yield Document(page_content=line, line_number=line_number)
                line_number += 1


loader = CustomDocumentLoader("./喵喵.txt")
documents = loader.load()
print(documents)
print(len(documents))
print(documents[0].metadata)
