#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 19.5.25 PM10:09
@Author  : tianshiyang
@File    : 2.configurable_fields替换提示词.py
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import ConfigurableField

prompt = PromptTemplate.from_template("请写一篇关于{subject}主题的冷笑话").configurable_fields(
    template=ConfigurableField(id="prompt_template")
)

content = prompt.invoke({
    "subject": "程序员",
}).to_string()

print(content)

# 方法一，在invoke的config中配置参数
# content2 = prompt.invoke({
#     "subject": "程序员"
# }, config={
#     "configurable": {
#         "prompt_template": "请写一篇关于{subject}主题的藏头诗"
#     }
# }).to_string()

# 方法2，使用with_config
with_config_prompt = prompt.with_config(configurable={
    "prompt_template": "请写一篇关于{subject}主题的藏头诗2"
})

content2 = with_config_prompt.invoke({
    "subject": "程序员",
}).to_string()

print(content2)
