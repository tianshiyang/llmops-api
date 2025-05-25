#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM6:52
@Author  : tianshiyang
@File    : 4.通用文档加载器.py
"""
from langchain_unstructured import UnstructuredLoader

loader = UnstructuredLoader("./项目API资料.md")
documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
