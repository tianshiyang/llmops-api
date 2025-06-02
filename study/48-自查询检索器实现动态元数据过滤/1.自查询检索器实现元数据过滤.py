#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.6.25 PM2:57
@Author  : tianshiyang
@File    : 1.自查询检索器实现元数据过滤.py
"""
import os

import dotenv
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers import SelfQueryRetriever
from langchain_core.documents import Document
import weaviate
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_weaviate import WeaviateVectorStore

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()

# 1.构建文档列表并上传到数据库
documents = [
    Document(
        page_content="肖申克的救赎",
        metadata={"year": 1994, "rating": 9.7, "director": "弗兰克·德拉邦特"},
    ),
    Document(
        page_content="霸王别姬",
        metadata={"year": 1993, "rating": 9.6, "director": "陈凯歌"},
    ),
    Document(
        page_content="阿甘正传",
        metadata={"year": 1994, "rating": 9.5, "director": "罗伯特·泽米吉斯"},
    ),
    Document(
        page_content="泰坦尼克号",
        metadat={"year": 1997, "rating": 9.5, "director": "詹姆斯·卡梅隆"},
    ),
    Document(
        page_content="千与千寻",
        metadat={"year": 2001, "rating": 9.4, "director": "宫崎骏"},
    ),
    Document(
        page_content="星际穿越",
        metadat={"year": 2014, "rating": 9.4, "director": "克里斯托弗·诺兰"},
    ),
    Document(
        page_content="忠犬八公的故事",
        metadat={"year": 2009, "rating": 9.4, "director": "莱塞·霍尔斯道姆"},
    ),
    Document(
        page_content="三傻大闹宝莱坞",
        metadat={"year": 2009, "rating": 9.2, "director": "拉库马·希拉尼"},
    ),
    Document(
        page_content="疯狂动物城",
        metadat={"year": 2016, "rating": 9.2, "director": "拜伦·霍华德"},
    ),
    Document(
        page_content="无间道",
        metadat={"year": 2002, "rating": 9.3, "director": "刘伟强"},
    ),
]

# client = weaviate.connect_to_weaviate_cloud(
#     cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
#     auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
# )

db = PineconeVectorStore(
    pinecone_api_key="pcsk_rcNxM_9QUxqQpez1eQzm6GYCW5k73CKxhRhERAmcwQegGLy8GrbcymEqHzJN2WR38idWy",
    index_name="llmops",
    text_key="text",
    embedding=DashScopeEmbeddings(),
    namespace="dataset",
)

db.add_documents(documents)

# 定义元数据
metadata_field_info = [
    AttributeInfo(
        name="year",
        description="电影的年份信息",
        type="integer"
    ),
    AttributeInfo(
        name="rating",
        description="电影的评分",
        type="float"
    ),
    AttributeInfo(
        name="director",
        description="电影的导演",
        type="string"
    )
]

retriever = db.as_retriever()

# 创建子查询检索器
self_query_retriever = SelfQueryRetriever.from_llm(
    llm=ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0),
    vectorstore=db,
    enable_limit=True,
    document_contents="电影的名字",
    metadata_field_info=metadata_field_info,
)

# 4.检索示例
docs = self_query_retriever.invoke("查找下评分高于9.5分的电影")
print(docs)
print(len(docs))
print("===================")
base_docs = retriever.invoke("查找下评分高于9.5分的电影")
print(base_docs)
print(len(base_docs))
