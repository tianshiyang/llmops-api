#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:19
@Author  : tianshiyang
@File    : 1.字符分割器使用示例.py
"""
from langchain_text_splitters import CharacterTextSplitter
from langchain_unstructured import UnstructuredLoader

loader = UnstructuredLoader("./项目API文档.md")
documents = loader.load()

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True
)

chunks = text_splitter.split_documents(documents)

for chunk in chunks:
    print(f"块大小{len(chunk.page_content)}, 元数据{chunk.metadata}")

print(len(chunks))
