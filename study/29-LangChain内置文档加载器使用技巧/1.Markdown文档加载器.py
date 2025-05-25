#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM6:51
@Author  : tianshiyang
@File    : 1.Markdown文档加载器.py
"""
from langchain_community.document_loaders import UnstructuredMarkdownLoader

loader = UnstructuredMarkdownLoader('./项目API资料.md', mode="elements")
documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].page_content)
