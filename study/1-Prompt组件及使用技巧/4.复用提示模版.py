#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/5 22:13
@Author  : tianshiyang
@File    : 4.复用提示模版.py
"""
from langchain_core.prompts import PromptTemplate, PipelinePromptTemplate

# 明确写出最终模板需要的3个字段
# full_template = PromptTemplate(
#     input_variables=["instruction", "example", "start"],
#     template="""
# {instruction}
#
# {example}
#
# {start}
# """)

full_template = PromptTemplate.from_template("""{instruction}

{example}

{start}""")

# 子模板
instruction_prompt = PromptTemplate.from_template("你正在模拟{person}")
example_prompt = PromptTemplate.from_template("""下面是一个交互例子：

Q: {example_q}
A: {example_a}""")
start_prompt = PromptTemplate.from_template("""现在，你是一个真实的人，请回答用户的问题:

Q: {input}
A:""")

# 管道 prompt
pipeline_prompt = PipelinePromptTemplate(
    final_prompt=full_template,
    pipeline_prompts=[
        ("instruction", instruction_prompt),
        ("example", example_prompt),
        ("start", start_prompt)
    ]
)

# 执行并输出
result = pipeline_prompt.invoke({
    "person": "雷军",
    "example_q": "你最喜欢的汽车是什么?",
    "example_a": "小米SU7",
    "input": "你最喜欢的手机是什么?"
})

print(result.to_string())
