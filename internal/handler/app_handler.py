#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.4.25 PM11:20
@Author  : 1685821150@qq.com
@File    : app_handler.py
"""
import uuid
from dataclasses import dataclass
from flask import request
from flask_login import login_required, current_user
from injector import inject
from internal.schema.app_schema import CreateAppReq, GetAppResp, GetPublishHistoriesWithPageReq, \
    GetPublishHistoriesWithPageResp, FallbackHistoryToDraftReq, UpdateDebugConversationSummaryReq
from internal.service import AppService

from pkg.paginator.paginator import PageModel
from pkg.response import success_json, validate_error_json, success_message


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService

    @login_required
    def create_app(self):
        """调用服务创建新的APP记录"""
        # 1.提取请求并校验
        req = CreateAppReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 2.调用服务创建应用信息
        app = self.app_service.create_app(req, current_user)
        # 3.返回创建成功响应提示
        return success_json({"id": app.id})

    @login_required
    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id, current_user)
        resp = GetAppResp()
        return success_json(resp.dump(app))

    @login_required
    def get_draft_app_config(self, app_id: uuid.UUID):
        """根据传递的应用id获取应用的最新草稿配置"""
        draft_config = self.app_service.get_draft_app_config(app_id, current_user)
        return success_json(draft_config)

    @login_required
    def update_draft_app_config(self, app_id: uuid.UUID):
        """根据传递的应用id+草稿配置更新应用的最新草稿配置"""
        # 1.获取草稿请求json数据
        draft_app_config = request.get_json(force=True, silent=True) or {}

        # 2.调用服务更新应用的草稿配置
        self.app_service.update_draft_app_config(app_id, draft_app_config, current_user)
        return success_message("更新应用草稿配置成功")

    @login_required
    def publish(self, app_id: uuid.UUID):
        """根据传递的应用id发布、更新特定的草稿配置信息"""
        self.app_service.publish_draft_app_config(app_id, current_user)
        return success_message("发布/更新应用配置成功")

    @login_required
    def cancel_publish(self, app_id: uuid.UUID):
        """根据传递的应用id，取消发布指定的应用配置信息"""
        self.app_service.cancel_publish_app_config(app_id, current_user)
        return success_message("取消发布应用配置成功")

    @login_required
    def get_publish_histories_with_page(self, app_id: uuid.UUID):
        """根据传递的应用id，获取应用发布历史列表"""
        # 1.获取请求数据并校验
        req = GetPublishHistoriesWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务获取分页列表数据
        app_config_versions, paginator = self.app_service.get_publish_histories_with_page(app_id, req, current_user)

        # 3. 创建响应结构并返回
        resp = GetPublishHistoriesWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(app_config_versions), paginator=paginator))

    @login_required
    def fallback_history_to_draft(self, app_id: uuid.UUID):
        """根据传递的应用id+历史配置版本id，回退指定版本到草稿中"""
        # 1.提取数据并校验
        req = FallbackHistoryToDraftReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务回退指定版本到草稿
        self.app_service.fallback_history_to_draft(app_id, req.app_config_version_id.data, current_user)
        return success_message("回退历史配置至草稿成功")

    @login_required
    def get_debug_conversation_summary(self, app_id: uuid.UUID):
        """根据传递的应用id获取调试会话长期记忆"""
        summary = self.app_service.get_debug_conversation_summary(app_id, current_user)
        return success_json({"summary": summary})

    @login_required
    def update_debug_conversation_summary(self, app_id: uuid.UUID):
        """根据传递的应用id+摘要信息更新调试会话长期记忆"""
        # 1.提取数据并校验
        req = UpdateDebugConversationSummaryReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务更新调试会话长期记忆
        self.app_service.update_debug_conversation_summary(app_id, req.summary.data, current_user)
        return success_message("更新AI应用长期记忆成功")

    # def ping(self):
    #     agent = FunctionCallAgent(AgentConfig(
    #         llm=ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL")),
    #         preset_prompt="你是一个拥有20年经验的诗人，请根据用户提供的主题写一首诗"
    #     ))
    #     state = agent.run("程序员", [], "")
    #     content = state['messages'][-1]['content']
    #     return success_json({"content": content})
    #
    # def _ping(self):
    #     # self.redis_client.set('name', 'zhangsan')
    #     # print(self.redis_client.get("name"))
    #     # result = demo_task.delay(uuid.uuid4())
    #     # value = {
    #     #     "token_count": self.embeddings_service.calculate_token_count("你好，你是谁"),
    #     #     # "embedding_value": self.embeddings_service.embeddings.embed_query("你好，你是谁")
    #     # }
    #     value = self.conversation_service.generate_suggested_questions("""
    #     LLM 就是一种通过训练大量文本数据、能理解和生成自然语言（甚至代码）的人工智能模型。你现在在用的 ChatGPT 就是基于 LLM 的产品之一。
    #
    #     🧠 LLM 能做什么？
    #     它具备以下能力：
    #
    #     自然语言理解与生成（写文章、摘要、改写、对话等）
    #
    #     代码生成与调试（如 Python、JavaScript、Java 等）
    #
    #     问答系统（像 ChatGPT、Claude、文心一言）
    #
    #     翻译、多语言支持
    #
    #     信息抽取（从文档中提取关键字段）
    #
    #     多模态能力（图像 + 文本，如 GPT-4o）
    #
    #     🔧 LLM 的工作原理（简略版）：
    #     预训练（Pretraining）：在大量文本（如 Wikipedia、书籍、网页）上进行语言建模。
    #
    #     微调（Fine-tuning）：根据具体任务（如问答、聊天）进一步训练。
    #
    #     推理（Inference）：用户输入一句话，模型基于上下文预测下一个最合理的词，一步步生成回答。""")
    #     return success_json({"ping": value})
    #
    # def debug(self, app_id: uuid.UUID):
    #     req = CompletionReq()
    #     if not req.validate():
    #         return validate_error_json(req.errors)
    #
    #     # 2. 创建队列并提取query数据
    #     q = Queue()
    #     query = req.query.data
    #
    #     # 3. 创建graph图应用程序
    #     def graph_app() -> None:
    #         """创建Graph图程序应用并执行"""
    #         # 3.1 创建tools工具列表
    #         tools = [
    #             self.builtin_provider_manager.get_tool('google', "google_serper")(),
    #             self.builtin_provider_manager.get_tool('gaode', "gaode_weather")(),
    #             self.builtin_provider_manager.get_tool('dalle', "dalle3")(),
    #         ]
    #
    #         # 3.2 定义大语言模型、聊天机器人节点
    #         def chatbot(state: MessagesState) -> MessagesState:
    #             """机器人聊天节点"""
    #             # 3.2.1创建LLM大语言模型
    #             llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0.7).bind_tools(tools)
    #
    #             # 3.2.2 调用stream()函数获取流式输出内容，并判断生成内容是文本还是工具调用函数
    #             is_first_chunk = True
    #             is_tool_call = False
    #             gathered = None
    #             id = str(uuid.uuid4())
    #             for chunk in llm.stream(state['messages']):
    #                 # 3.2.3检测是不是第一个块，部分LLM的第一个块不会输出内容，需要抛弃掉
    #                 if is_first_chunk and chunk.content == "" and not chunk.tool_calls:
    #                     continue
    #
    #                 # 3.2.4 叠加相应的区块
    #                 if is_first_chunk:
    #                     gathered = chunk
    #                     print(chunk, 'chunk是这个')
    #                     is_first_chunk = False
    #                 else:
    #                     gathered += chunk
    #
    #                 # 3.2.5 判断是工具调用还是文本生成，往队列中添加不同的数据
    #                 if chunk.tool_calls or is_tool_call:
    #                     is_tool_call = True
    #                     q.put({
    #                         "id": id,
    #                         "event": "agent_thought",
    #                         "data": json.dumps(chunk.tool_call_chunks)
    #                     })
    #                 else:
    #                     q.put({
    #                         "id": id,
    #                         "event": "agent_message",
    #                         "data": json.dumps(chunk.content)
    #                     })
    #             return {"messages": [gathered]}
    #
    #         # 3.3 定义工具、函数调用节点
    #         def tool_executor(state: MessagesState) -> MessagesState:
    #             # 工具执行节点
    #             # 3.3.1 提取数据状态中的tool_calls
    #             tool_calls = state['messages'][-1].tool_calls
    #
    #             # 3.3.2 将工具列表转换为字典便于使用
    #             tools_by_name = {tool.name: tool for tool in tools}
    #
    #             # 3.3.3 执行工具并得到对应结果
    #             messages = []
    #             for tool_call in tool_calls:
    #                 id = str(uuid.uuid4())
    #                 tool = tools_by_name[tool_call['name']]
    #                 tool_result = tool.invoke(tool_call['args'])
    #                 print(tool_result, 'tool_result====')
    #                 messages.append(ToolMessage(
    #                     tool_call_id=tool_call['id'],
    #                     content=json.dumps(tool_result),
    #                     name=tool_call['name']
    #                 ))
    #                 q.put({
    #                     "id": id,
    #                     "event": "agent_action",
    #                     "data": json.dumps(tool_result)
    #                 })
    #             return {"messages": messages}
    #
    #         # 3.4定义路由函数
    #         def route(state: MessagesState) -> Literal["tool_executor", "__end__"]:
    #             """定义路由节点，确认下一步步骤"""
    #             ai_message = state["messages"][-1]
    #             if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
    #                 return "tool_executor"
    #             return END
    #
    #         # 3.5 创建状态图
    #         graph_builder = StateGraph(MessagesState)
    #
    #         # 3.6 添加节点
    #         graph_builder.add_node("llm", chatbot)
    #         graph_builder.add_node("tool_executor", tool_executor)
    #
    #         # 3.7 添加边
    #         graph_builder.set_entry_point("llm")
    #         graph_builder.add_conditional_edges("llm", route)
    #         graph_builder.add_edge("tool_executor", "llm")
    #
    #         # 3.8编译图程序为可运行组件
    #         graph = graph_builder.compile()
    #
    #         # 3.9 调用图结构程序并获取结果
    #         result = graph.invoke({"messages": [("human", query)]})
    #         print("最终结果: ", result)
    #         q.put(None)
    #
    #     def stream_event_response() -> Generator:
    #         """流式事件输出响应"""
    #         # 1. 从队列中获取数据并使用yield抛出
    #         while True:
    #             item = q.get()
    #             if item is None:
    #                 break
    #             # 2. 使用yield关键字返回对应的数据
    #             yield f"event: {item.get('event')}\ndata: {json.dumps(item)}\n\n"
    #             q.task_done()
    #
    #     t = Thread(target=graph_app)
    #     t.start()
    #
    #     return compact_generate_response(stream_event_response())
