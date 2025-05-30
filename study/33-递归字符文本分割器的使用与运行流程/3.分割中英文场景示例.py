#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:20
@Author  : tianshiyang
@File    : 3.分割中英文场景示例.py
"""
from langchain_text_splitters import TextSplitter, RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader

separators = [
    "\n\n",
    "\n",
    "。|！|？",
    "\.\s|\!\s|\?\s",  # 英文标点符号后面通常需要加空格
    "；|;\s",
    "，|,\s",
    " ",
    ""
]

documents = UnstructuredLoader("./项目API文档.md").load()

text_splitter = RecursiveCharacterTextSplitter(
    separators=separators,
    is_separator_regex=True,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True
)

chunks = text_splitter.split_documents(documents)

for chunk in chunks:
    print(f"块大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

print(chunks[2].page_content)
