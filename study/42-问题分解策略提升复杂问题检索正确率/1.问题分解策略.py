#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 29.5.25 PM10:24
@Author  : tianshiyang
@File    : 1.问题分解策略.py
"""
import os
from operator import itemgetter

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
import weaviate
from langchain_weaviate import WeaviateVectorStore

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()


def format_qa_pair(question: str, answer: str) -> str:
    """格式化传递的问题+答案为单个字符串"""
    return f"Question: {question}\nAnswer: {answer}\n\n".strip()


# 1.定义分解子问题的prompt
decomposition_prompt = ChatPromptTemplate.from_template("""
    你是一个乐于助人的AI助理，可以针对一个输入问题生成多个相关的子问题。
    目标是将输入问题分解成一组可以独立回答的子问题或者子任务。
    生成与一下问题相关的多个搜索查询：{question}
    并使用换行符进行分割，输出（3个子问题/子查询）：
""")

# 2.构建分解问题链

decomposition_chain = (
        {"question": RunnablePassthrough()} |
        decomposition_prompt |
        ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL")) |
        StrOutputParser() |
        (lambda x: x.strip().split("\n"))
)

# 3.构建向量数据库与检索器
client = weaviate.connect_to_weaviate_cloud(
    cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
)
embedding = DashScopeEmbeddings()
db = WeaviateVectorStore(
    client=client,
    index_name="DatasetDemo",
    text_key="text",
    embedding=embedding,
)
retriever = db.as_retriever(search_type="mmr")

# 4.执行提问获取子问题
question = "关于LLMOps应用配置的文档有哪些"
sub_questions = decomposition_chain.invoke(question)

# 5.构建迭代问答链：提示模板+链
prompt = ChatPromptTemplate.from_template("""
这是你需要回答的问题：
---
{question}
---

这是所有可用的背景问题和答案对：
---
{qa_pairs}
---

这是与问题相关的额外背景信息：
---
{context}
---
""")

chain = (
        {
            "question": itemgetter("question"),
            "qa_pairs": itemgetter("qa_pairs"),
            # "context": RunnableLambda(lambda x: x["question"]) | retriever,
            "context": itemgetter("question") | retriever,
        }
        | prompt
        | ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0)
        | StrOutputParser()
)

# 6.循环遍历所有子问题进行检索并获取答案

qa_pairs = ""
for question in sub_questions:
    answer = chain.invoke({
        "question": question,
        "qa_pairs": qa_pairs,
    })
    qa_pairs += ("\n---\n" + qa_pairs + format_qa_pair(question, answer))
    print(f"问题: {question}")
    print(f"答案: {answer}")

client.close()
