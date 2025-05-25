#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM6:52
@Author  : tianshiyang
@File    : 3.URL网页加载器.py
"""
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://imooc.com")
documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
