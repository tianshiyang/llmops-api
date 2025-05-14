#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.4.25 PM11:20
@Author  : 1685821150@qq.com
@File    : app_handler.py
"""
import os
import uuid
from dataclasses import dataclass
from operator import itemgetter

from flask import request
from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
    MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI

from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import success_json, validate_error_json, success_message


@inject
@dataclass
class AppHandler:
    """应用控制器"""

    app_service: AppService

    def debug(self, app_id):
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 1. 创建prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("你是openai开发的聊天机器人，请根据上下文回答问题"),
            MessagesPlaceholder("history"),
            HumanMessagePromptTemplate.from_template("{query}")
        ])
        # 2. 创建llm大语言模型
        llm = ChatOpenAI(model="moonshot-v1-8k")
        # 3. 创建记忆
        memory = ConversationBufferWindowMemory(
            k=3,
            input_key="query",
            output_key="output",
            return_messages=True,
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt")
        )
        # 4. 创建链
        chain = RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        ) | prompt | llm | StrOutputParser()

        chain_input = {"query": req.query.data}
        content = chain.invoke(chain_input)
        memory.save_context(chain_input, outputs={"output": content})
        return success_json({"content": content})

    def create_app(self):
        app = self.app_service.create_app()
        return success_message(f"应用创建成功，id为{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用已经成功获取，名字是{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用名称修改成功，修改后的名字是{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"应用已经成功删除，id为:{app.id}")

    def completion(self):
        """聊天接口"""
        # 1.提取从接口中获取的输入，POST
        json_data = request.get_json()
        req = CompletionReq(data=json_data)
        if not req.validate():
            print(req.errors)
            return validate_error_json(req.errors)

        # 2.构建OpenAI客户端，并发起请求
        # client = OpenAI(
        #     api_key=os.getenv('OPENAI_API_KEY'),
        #     base_url=os.getenv('OPENAI_BASE_URL'),
        # )
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("你是OpenAI开发的聊天机器人，请根据用户的输入回复对应的信息"),
            HumanMessagePromptTemplate.from_template("{query}")
        ])

        llm = ChatOpenAI(model="moonshot-v1-8k")

        parser = StrOutputParser()

        content = prompt | llm | parser
        # completion = client.chat.completions.create(
        #     model="moonshot-v1-8k",
        #     messages=[
        #         {"role": "system",
        #          "content": "你是OpenAI开发的聊天机器人，请根据用户的输入回复对应的信息"},
        #         {"role": "user", "content": req.query.data}
        #     ],
        #     temperature=0.3,
        # )
        return success_json({"content": content.invoke(json_data['query'])})

    def ping(self):
        return success_json({"ping": "pong"})
