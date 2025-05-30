#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 29.5.25 PM10:25
@Author  : tianshiyang
@File    : 2.回答回退策略检索器.py
"""
import os
from operator import itemgetter
from typing import List

import dotenv
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.retrievers import BaseRetriever
import weaviate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_weaviate import WeaviateVectorStore

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()


class StepBackRetriever(BaseRetriever):
    llm: BaseLanguageModel
    retriever: BaseRetriever

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        examples = [
            {"input": "慕课网上有关于AI应用开发的课程吗？", "output": "慕课网上有哪些课程？"},
            {"input": "慕小课出生在哪个国家？", "output": "慕小课的人生经历是什么样的？"},
            {"input": "司机可以开快车吗？", "output": "司机可以做什么？"},
        ]
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}"),
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
        )

        # 构建真实模版
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是一个世界知识的专家。你的任务是回退问题，将问题改述为更一般或者前置问题，这样更容易回答，请参考示例来实现。"),
            few_shot_prompt,
            ("ai", "{question}"),
        ])

        chain = {
                    "question": RunnablePassthrough()
                } | prompt | self.llm | StrOutputParser() | self.retriever

        return chain.invoke(query)


embedding = DashScopeEmbeddings()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
)

retriever = WeaviateVectorStore(
    client=client,
    embedding=embedding,
    text_key="text",
    index_name="DatasetDemo"
).as_retriever(search_type="mmr")

step_back_retriever = StepBackRetriever(
    retriever=retriever,
    llm=ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0)
)

documents = step_back_retriever.invoke("人工智能会让世界发生翻天覆地的变化吗？")
print(documents)
print(len(documents))

client.close()
