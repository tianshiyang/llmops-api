#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:19
@Author  : tianshiyang
@File    : 2.2.其他文档分割器使用示例.py
"""
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter, Language
from langchain_unstructured import UnstructuredLoader

documents = UnstructuredLoader("./demo.py").load()

text_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True
)

chunks = text_splitter.split_documents(documents)
for chunk in chunks:
    print(f"块大小: {chunk.page_content}, 元数据: {chunk.metadata}")

print(chunks[2].page_content)
