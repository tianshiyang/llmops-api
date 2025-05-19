#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 19.5.25 PM10:11
@Author  : tianshiyang
@File    : 1.Runnable重试机制.py
"""
from langchain_core.runnables import RunnableLambda

count = -1


def func(num):
    global count
    count += 1
    print(f'当前值{count}')
    return num / count


chain = RunnableLambda(func).with_retry(stop_after_attempt=2)

content = chain.invoke(2)
print(content)
