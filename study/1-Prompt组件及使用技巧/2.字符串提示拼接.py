#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/5 22:13
@Author  : tianshiyang
@File    : 2.字符串提示拼接.py
"""
from langchain_core.prompts import PromptTemplate

prompt = (
        PromptTemplate.from_template("请讲一个关于{subject}的冷笑话")
        + ",让我开心下" +
        "\n使用{language}语言"
)

prompt_value = prompt.invoke({
    "subject": "哈哈哈",
    "language": "中文",
})

print(prompt_value.to_string())
