#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:21
@Author  : tianshiyang
@File    : 1.语义分割器使用示例.py
"""
from langchain_experimental.text_splitter import SemanticChunker
from langchain_unstructured import UnstructuredLoader
from custom_embeddings import DashScopeEmbeddings

documents = UnstructuredLoader("./科幻短篇.txt").load()

# 1.创建文本嵌入模型
embeddings = DashScopeEmbeddings()

text_splitter = SemanticChunker(
    embeddings=embeddings,
    add_start_index=True,
    number_of_chunks=10,  # 最终期望将文本分成多少段
    sentence_split_regex=r"(?<=[。？！.?!])"  # 自定义的正则表达式，用于先将文本拆成句子，后续再基于语义进行聚类
)

chunks = text_splitter.split_documents(documents)

# 3.循环打印
for chunk in chunks:
    print(f"块大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")
