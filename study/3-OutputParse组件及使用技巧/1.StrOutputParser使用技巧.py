#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/7 11:46
@Author  : tianshiyang
@File    : 1.StrOutputParser使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.编排提示模板
prompt = ChatPromptTemplate.from_template("{query}")

# 2.构建大语言模型
llm = ChatOpenAI(model="moonshot-v1-8k")

# 3.创建字符串输出解析器
parser = StrOutputParser()

# 4.调用大语言模型生成结果并解析
# 写法一
# content = parser.invoke(llm.invoke(prompt.invoke({"query": "你好，你是?"})))
# 写法二
content = prompt | llm | parser

print(content.invoke({"query": "你好，你是"}))
