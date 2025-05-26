#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:21
@Author  : tianshiyang
@File    : 2.其他文档分割器使用示例.py
"""
from langchain_text_splitters import HTMLHeaderTextSplitter

# 1.构建文本与分割标题
html_string = """
<!DOCTYPE html>
<html>
<body>
    <div>
        <h1>标题1</h1>
        <p>关于标题1的一些介绍文本。</p>
        <div>
            <h2>子标题1</h2>
            <p>关于子标题1的一些介绍文本。</p>
            <h3>子子标题1</h3>
            <p>关于子子标题1的一些文本。</p>
            <h3>子子标题2</h3>
            <p>关于子子标题2的一些文本。</p>
        </div>
        <div>
            <h3>子标题2</h2>
            <p>关于子标题2的一些文本。</p>
        </div>
        <br>
        <p>关于标题1的一些结束文本。</p>
    </div>
</body>
</html>
"""

headers_to_split_on = [
    ("h1", "标题1"),
    ("h2", "标题2"),
    ("h3", "标题3"),
]

text_splitter = HTMLHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
)

chunks = text_splitter.split_text(html_string)

# 3.输出分割内容
for chunk in chunks:
    print(chunk)
