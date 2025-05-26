#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:21
@Author  : tianshiyang
@File    : 3.分割中英文场景示例.py
"""
import requests
from langchain_text_splitters import HTMLHeaderTextSplitter, RecursiveJsonSplitter

url = "https://api.smith.langchain.com/openapi.json"
json = requests.get(url).json()

text_splitter = RecursiveJsonSplitter(max_chunk_size=300)
json_chunks = text_splitter.split_json(json)

documents = text_splitter.create_documents(json_chunks)

for document in documents:
    print(document)
