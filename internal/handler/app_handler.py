#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.4.25 PM11:20
@Author  : 1685821150@qq.com
@File    : app_handler.py
"""
import json
import os
import uuid
from dataclasses import dataclass
from operator import itemgetter
from queue import Queue
from threading import Thread
from typing import Literal, Annotated, Generator

from flask import request
from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
    MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState
from redis import Redis
from langgraph.constants import END

from internal.core.tools.builtin_tools.providers.builtin_provider_manager import BuiltinProviderManager
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from internal.service.embeddings_service import EmbeddingsService
from internal.task.demo_task import demo_task
from pkg.response import success_json, validate_error_json, success_message
from pkg.response.response import compact_generate_response


@inject
@dataclass
class AppHandler:
    """应用控制器"""

    app_service: AppService
    redis_client: Redis
    embeddings_service: EmbeddingsService
    builtin_provider_manager: BuiltinProviderManager

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
        # self.redis_client.set('name', 'zhangsan')
        # print(self.redis_client.get("name"))
        result = demo_task.delay(uuid.uuid4())
        value = {
            "token_count": self.embeddings_service.calculate_token_count("你好，你是谁"),
            # "embedding_value": self.embeddings_service.embeddings.embed_query("你好，你是谁")
        }
        return success_json({"ping": value})

    def debug(self, app_id: uuid.UUID):
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 创建队列并提取query数据
        q = Queue()
        query = req.query.data

        # 3. 创建graph图应用程序
        def graph_app() -> None:
            """创建Graph图程序应用并执行"""
            # 3.1 创建tools工具列表
            tools = [
                self.builtin_provider_manager.get_tool('google', "google_serper")(),
                self.builtin_provider_manager.get_tool('gaode', "gaode_weather")(),
                self.builtin_provider_manager.get_tool('dalle', "dalle3")(),
            ]

            # 3.2 定义大语言模型、聊天机器人节点
            def chatbot(state: MessagesState) -> MessagesState:
                """机器人聊天节点"""
                # 3.2.1创建LLM大语言模型
                llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0.7).bind_tools(tools)

                # 3.2.2 调用stream()函数获取流式输出内容，并判断生成内容是文本还是工具调用函数
                is_first_chunk = True
                is_tool_call = False
                gathered = None
                id = str(uuid.uuid4())
                for chunk in llm.stream(state['messages']):
                    # 3.2.3检测是不是第一个块，部分LLM的第一个块不会输出内容，需要抛弃掉
                    if is_first_chunk and chunk.content == "" and not chunk.tool_calls:
                        continue

                    # 3.2.4 叠加相应的区块
                    if is_first_chunk:
                        gathered = chunk
                        print(chunk, 'chunk是这个')
                        is_first_chunk = False
                    else:
                        gathered += chunk

                    # 3.2.5 判断是工具调用还是文本生成，往队列中添加不同的数据
                    if chunk.tool_calls or is_tool_call:
                        is_tool_call = True
                        q.put({
                            "id": id,
                            "event": "agent_thought",
                            "data": json.dumps(chunk.tool_call_chunks)
                        })
                    else:
                        q.put({
                            "id": id,
                            "event": "agent_message",
                            "data": json.dumps(chunk.content)
                        })
                return {"messages": [gathered]}

            # 3.3 定义工具、函数调用节点
            def tool_executor(state: MessagesState) -> MessagesState:
                # 工具执行节点
                # 3.3.1 提取数据状态中的tool_calls
                tool_calls = state['messages'][-1].tool_calls

                # 3.3.2 将工具列表转换为字典便于使用
                tools_by_name = {tool.name: tool for tool in tools}

                # 3.3.3 执行工具并得到对应结果
                messages = []
                for tool_call in tool_calls:
                    id = str(uuid.uuid4())
                    tool = tools_by_name[tool_call['name']]
                    tool_result = tool.invoke(tool_call['args'])
                    print(tool_result, 'tool_result====')
                    messages.append(ToolMessage(
                        tool_call_id=tool_call['id'],
                        content=json.dumps(tool_result),
                        name=tool_call['name']
                    ))
                    q.put({
                        "id": id,
                        "event": "agent_action",
                        "data": json.dumps(tool_result)
                    })
                return {"messages": messages}

            # 3.4定义路由函数
            def route(state: MessagesState) -> Literal["tool_executor", "__end__"]:
                """定义路由节点，确认下一步步骤"""
                ai_message = state["messages"][-1]
                if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
                    return "tool_executor"
                return END

            # 3.5 创建状态图
            graph_builder = StateGraph(MessagesState)

            # 3.6 添加节点
            graph_builder.add_node("llm", chatbot)
            graph_builder.add_node("tool_executor", tool_executor)

            # 3.7 添加边
            graph_builder.set_entry_point("llm")
            graph_builder.add_conditional_edges("llm", route)
            graph_builder.add_edge("tool_executor", "llm")

            # 3.8编译图程序为可运行组件
            graph = graph_builder.compile()

            # 3.9 调用图结构程序并获取结果
            result = graph.invoke({"messages": [("human", query)]})
            print("最终结果: ", result)
            q.put(None)

        def stream_event_response() -> Generator:
            """流式事件输出响应"""
            # 1. 从队列中获取数据并使用yield抛出
            while True:
                item = q.get()
                if item is None:
                    break
                # 2. 使用yield关键字返回对应的数据
                yield f"event: {item.get('event')}\ndata: {json.dumps(item)}\n\n"
                q.task_done()

        t = Thread(target=graph_app)
        t.start()

        return compact_generate_response(stream_event_response())
