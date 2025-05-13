#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/11 22:41
@Author  : tianshiyang
@File    : 1.缓冲记忆窗口示例.py
"""
from operator import itemgetter
import dotenv
from langchain.memory import ConversationTokenBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAi开发的聊天机器人，请根据对应的上下文回答用户的问题"),
    MessagesPlaceholder("history"),  # 需要的history其实是一个列表
    ("human", "{query}")
])

memory = ConversationTokenBufferMemory(
    return_messages=True,
    input_key="query",
    llm=ChatOpenAI()
)

llm = ChatOpenAI(model="moonshot-v1-8k")

chain = RunnablePassthrough.assign(
    history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
) | prompt | llm | StrOutputParser()

while True:
    query = input("human:")
    if query == "q":
        break
    chain_input = {
        "query": query,
        "language": "中文",
    }
    response = chain.stream(chain_input)
    print("AI: ", flush=True, end="")
    output = ""
    for chunk in response:
        output += chunk
        print(chunk, flush=True, end="")
    memory.save_context(chain_input, {"output": output})
    print("")
    print("history: ", memory.load_memory_variables({})['history'])
