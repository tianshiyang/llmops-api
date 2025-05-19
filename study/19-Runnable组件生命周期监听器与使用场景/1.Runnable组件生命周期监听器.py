#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 19.5.25 PM10:12
@Author  : tianshiyang
@File    : 1.Runnable组件生命周期监听器.py
"""
import time

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tracers.schemas import Run


def on_start(run_obj: Run, config: RunnableConfig):
    print("on_start")
    print(f"run_obj:{run_obj}")
    print(f"config:{config}")
    print("============")


def on_end(run_obj: Run, config: RunnableConfig):
    print("on_end")
    print(f"run_obj:{run_obj}")
    print(f"config:{config}")
    print("============")


def on_error(run_obj: Run, config: RunnableConfig) -> None:
    print("on_error")
    print("run_obj:", run_obj)
    print("config:", config)
    print("============")


chain = RunnableLambda(lambda x: time.sleep(x)).with_listeners(
    on_start=on_start,
    on_end=on_end,
    on_error=on_error,
)

chain.invoke(2, config={"configurable": {"name": "慕小课"}})
