#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 29.5.25 PM10:25
@Author  : tianshiyang
@File    : 1.少量示例提示模版.py
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate, \
    FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

example_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("{question}"),
    AIMessagePromptTemplate.from_template("{answer}"),
])

examples = [
    {"question": "帮我计算下2+2等于多少？", "answer": "4"},
    {"question": "帮我计算下2+3等于多少？", "answer": "5"},
    {"question": "帮我计算下20*15等于多少？", "answer": "300"},
]

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

print(few_shot_prompt)
print(HumanMessagePromptTemplate.from_template("{question}"), )

# 3.构建最终提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个可以计算复杂数学问题的聊天机器人"),
    few_shot_prompt,
    ("human", "{question}"),
])

chain = prompt | ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0) | StrOutputParser()

print(chain.invoke({
    "question": "帮我计算下14*15等于多少"
}))
