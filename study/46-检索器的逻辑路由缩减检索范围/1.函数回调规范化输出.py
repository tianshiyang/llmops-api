#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.6.25 PM2:56
@Author  : tianshiyang
@File    : 1.函数回调规范化输出.py
"""
import os
from typing import Literal

import dotenv
from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field

# from pydantic import BaseModel, Field

dotenv.load_dotenv()


class RouteQuery(BaseModel):
    datasource: Literal["python_docs", "javascript_docs", "golang_docs"] = Field(
        description="根据用户提问，选择哪个数据源最相关以回答用户的提问"
    )


# 1. 创建绑定结构化输出的大语言模型
llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0)

structured_llm = llm.with_structured_output(RouteQuery)
question = """为什么下面的代码不工作了，请帮我检查下：

var a = "123"
"""

res = structured_llm.invoke(question)

print(res)
print(type(res))
print(res.datasource)
