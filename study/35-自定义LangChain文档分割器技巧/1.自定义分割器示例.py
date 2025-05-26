#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:23
@Author  : tianshiyang
@File    : 1.自定义分割器示例.py
"""
import jieba.analyse
from langchain_text_splitters import TextSplitter
from langchain_unstructured import UnstructuredLoader


class CustomTextSplitter(TextSplitter):
    def __init__(self, seperator: str, top_k: int = 10, **kwargs):
        super().__init__(**kwargs)
        self._seperator = seperator
        self._top_k = top_k

    def split_text(self, text: str) -> list[str]:
        split_texts = text.split(self._seperator)
        text_keywords = []
        for split_text in split_texts:
            text_keywords.append(jieba.analyse.extract_tags(split_text, self._top_k))
        return [",".join(keywords) for keywords in text_keywords]


# 1.创建加载器与分割器
loader = UnstructuredLoader("./科幻短篇.txt")
text_splitter = CustomTextSplitter("\n\n", 10)
# 2.加载文档并分割
documents = loader.load()
chunks = text_splitter.split_documents(documents)
# 3.循环遍历文档信息
for chunk in chunks:
    print(chunk.page_content)
