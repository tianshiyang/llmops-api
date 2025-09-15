#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 11.8.25 PM5:36
@Author  : tianshiyang
@File    : app_entity.py
"""
from enum import Enum

# 生成icon描述提示词模板
GENERATE_ICON_PROMPT_TEMPLATE = """你是一个拥有10年经验的AI绘画工程师，可以将用户传递的`应用名称`和`应用描述`转换为对应应用的icon描述。
该描述主要用于DallE AI绘画，并且该描述是英文，用户传递的数据如下:

应用名称: {name}。
应用描述: {description}。

并且除了icon描述提示词外，其他什么都不要生成"""


class AppStatus(str, Enum):
    """应用状态枚举类"""
    DRAFT = "draft"
    PUBLISHED = "published"


class AppConfigType(Enum):
    """应用配置类型枚举类"""
    DRAFT = "draft"
    PUBLISHED = "published"


# 应用默认配置信息
DEFAULT_APP_CONFIG = {
    "model_config": {
        "provider": "moonshot",  # 服务提供商
        "model": "moonshot-v1-8k",  # 默认模型
        "parameters": {
            "temperature": 0.5,  # 温度
            "top_p": 0.85,  # 前n个
            "frequency_penalty": 0.2,  # 频率惩罚 作用词汇级，避免词语过度重复
            "presence_penalty": 0.2,  # 存在惩罚 作用主题、字句，目的：避免重复讨论相同话题
            "max_tokens": 8192  # 最大回复长度
        },
    },
    "dialog_round": 3,  # 携带的上下轮轮数
    "preset_prompt": "",  # 预设提示词
    "tools": [],  # 工具列表
    "workflows": [],  # 工作流
    "datasets": [],  # 知识库,
    "retrieval_config": {
        "retrieval_strategy": "semantic",  # 检索策略
        "k": 10,  # 最大召回数量
        "score": 0.5  # 最小匹配度(得分)
    },
    "long_term_memory": {  # 长期记忆
        "enable": False,
    },
    "opening_statement": "",  # 开场白文案
    "opening_questions": [],  # 开场白预设问题
    "speech_to_text": {  # 开启语音输入
        "enable": False
    },
    "text_to_speech": {  # 开启语音输出
        "enable": False
    },
    "suggested_after_answer": {  # 回答后生成建议问题
        "enable": False
    },
    "review_config": {  # 内容审查
        "enable": False,
        "keywords": [],  # 关键词
        "inputs_config": {
            "enable": False,  # 开启审查输入内容
            "preset_response": "",  # 预设回复
        },
        "outputs_config": {  # 开启审查输出内容
            "enable": False,
        }
    }
}
