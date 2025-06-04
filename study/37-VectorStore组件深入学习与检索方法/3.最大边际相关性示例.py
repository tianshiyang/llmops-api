#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:25
@Author  : tianshiyang
@File    : 3.最大边际相关性示例.py
"""
# MMR（最大边际相关性）让你的检索结果不仅相关，而且不重复，让语言模型有“丰富、有用、少废话”的输入，是 RAG 中非常实用的检索策略。
import dotenv
import weaviate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader
from langchain_weaviate import WeaviateVectorStore

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()

documents = UnstructuredLoader("项目API文档.md").load()
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "。|！|？", "\.\s|\!\s|\?\s", "；|;\s", "，|,\s", " ", "", ],
    is_separator_regex=True,
    add_start_index=True,
    chunk_size=500,
    chunk_overlap=50
)

embedding = DashScopeEmbeddings()

docs = text_splitter.split_documents(documents)

client = weaviate.connect_to_weaviate_cloud(
    cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
)
db = WeaviateVectorStore(
    client=client,
    text_key="text",
    embedding=embedding,
    index_name="DatasetDemo"
)

result = db.max_marginal_relevance_search(query="关于应用配置的接口有哪些?")

print(len(result))

client.close()
for res in result:
    print(res.page_content)
