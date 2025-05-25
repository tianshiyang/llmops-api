#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM6:51
@Author  : tianshiyang
@File    : 1.Document组件与TextLoader.py
"""
from langchain_community.document_loaders import TextLoader

loader = TextLoader("./电商产品数据.txt")

result = loader.load()
print(result)
print(len(result))
print(result[0].metadata)
