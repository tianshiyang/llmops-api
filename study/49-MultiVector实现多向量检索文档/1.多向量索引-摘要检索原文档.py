#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.6.25 PM2:58
@Author  : tianshiyang
@File    : 1.多向量索引-摘要检索原文档.py
"""
import os
import uuid

import dotenv
from langchain.retrievers import MultiVectorRetriever
from langchain.storage import LocalFileStore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()

documents = UnstructuredLoader('./电商产品数据.txt').load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# 2.定义摘要生成链
summary_chain = (
        {"doc": lambda x: x.page_content}
        | ChatPromptTemplate.from_template("请总结以下文档的内容: {doc}")
        | ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"))
        | StrOutputParser()
)

# 3.批量生成摘要与唯一标识
summaries = summary_chain.batch(docs, {"max_concurrency": 5})
print(summaries, 'summaries')
doc_ids = [str(uuid.uuid4()) for _ in summaries]

# 4.构建摘要文档
summary_docs = [
    Document(page_content=summary, metadata={"doc_id": doc_ids[idx]})
    for idx, summary in enumerate(summaries)
]

# 5.构建文档数据库与向量数据库
byte_store = LocalFileStore("./multy-vector")
db = FAISS.from_documents(
    summary_docs,
    embedding=DashScopeEmbeddings(),
)

# 6.构建多向量检索器
retriever = MultiVectorRetriever(
    vectorstore=db,
    # byte_store=byte_store,
    id_key="doc_id",
    docstore=byte_store
)

# 7.将摘要文档和原文档存储到数据库中
retriever.docstore.mset(list(zip(doc_ids, docs)))

# 8.执行检索
search_docs = retriever.invoke("推荐一些潮州特产?")
print(search_docs)
print(len(search_docs))
