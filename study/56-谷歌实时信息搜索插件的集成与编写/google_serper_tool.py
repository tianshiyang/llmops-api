#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.6.25 PM6:32
@Author  : tianshiyang
@File    : google_serper_tool.py
"""
from typing import Any, Type

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


google_serper = GoogleSerperRun(
    name="google_serper_tool",
    description="这是一个调用谷歌搜索引擎的tool，当你需要进行联网搜索的时候，可以调用此工具",
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper()
)

print(google_serper.invoke("马拉松的世界记录是多少?"))
