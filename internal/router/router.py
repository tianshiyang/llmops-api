#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.4.25 PM11:38
@Author  : 1685821150@qq.com
@File    : router.py
"""
from dataclasses import dataclass

from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler, BuiltinToolHandler, ApiToolHandler, UploadFileHandler, DatasetHandler, \
    SegmentHandler, OAuthHandler, AuthHandler, AccountHandler, AiHandler, DocumentHandler, ApiKeyHandler, \
    OpenAPIHandler, BuiltinAppHandler, LanguageModelHandler, AssistantAgentHandler, AnalysisHandler, WebAppHandler, \
    ConversationHandler
from internal.handler.workflow_handler import WorkflowHandler


@inject
@dataclass
class Router:
    """"路由"""

    app_handler: AppHandler
    analysis_handler: AnalysisHandler
    builtin_tool_handler: BuiltinToolHandler
    api_tool_handler: ApiToolHandler
    upload_file_handler: UploadFileHandler
    dataset_handler: DatasetHandler
    document_handler: DocumentHandler
    segment_handler: SegmentHandler
    oauth_handler: OAuthHandler
    auth_handler: AuthHandler
    account_handler: AccountHandler
    ai_handler: AiHandler
    api_key_handler: ApiKeyHandler
    openapi_handler: OpenAPIHandler
    builtin_app_handler: BuiltinAppHandler
    workflow_handler: WorkflowHandler
    language_model_handler: LanguageModelHandler
    assistant_agent_handler: AssistantAgentHandler
    web_app_handler: WebAppHandler
    conversation_handler: ConversationHandler

    def register_router(self, app: Flask):
        """注册路由"""
        # 1. 创建一个蓝图（一组路由的集合）
        bp = Blueprint('llmops', __name__, url_prefix='')
        openapi_bp = Blueprint("openapi", __name__, url_prefix="")

        # 2. 将url与对应的控制器方法做绑定
        # bp.add_url_rule('/apps/<uuid:app_id>/debug', view_func=self.app_handler.debug, methods=['POST'])
        # 2.15 获取当前登录账号的应用分页列表数据
        bp.add_url_rule("/apps", view_func=self.app_handler.get_apps_with_page)
        # 2.16 根据传递的信息更新指定的应用
        bp.add_url_rule("/apps/<uuid:app_id>", methods=["POST"], view_func=self.app_handler.update_app)
        # 2.17 删除app
        bp.add_url_rule("/apps/<uuid:app_id>/delete", methods=["POST"], view_func=self.app_handler.delete_app)
        # 2.18 根据传递的应用id快速拷贝该应用
        bp.add_url_rule("/apps/<uuid:app_id>/copy", methods=["POST"], view_func=self.app_handler.copy_app)
        # 2.1 创建应用
        bp.add_url_rule('/apps', methods=["POST"], view_func=self.app_handler.create_app)
        # 2.2 获取应用
        bp.add_url_rule('/apps/<uuid:app_id>', view_func=self.app_handler.get_app)
        # 2.3 获取草稿配置
        bp.add_url_rule("/apps/<uuid:app_id>/draft-app-config", view_func=self.app_handler.get_draft_app_config)
        # 2.4 更新草稿配置
        bp.add_url_rule(
            "/apps/<uuid:app_id>/draft-app-config",
            methods=["POST"],
            view_func=self.app_handler.update_draft_app_config,
        )
        # 2.5 发布应用草稿配置信息
        bp.add_url_rule(
            "/apps/<uuid:app_id>/publish",
            methods=["POST"],
            view_func=self.app_handler.publish,
        )
        # 2.6 取消发布
        bp.add_url_rule(
            "/apps/<uuid:app_id>/cancel-publish",
            methods=["POST"],
            view_func=self.app_handler.cancel_publish,
        )
        # 2.7 获取发布历史
        bp.add_url_rule(
            "/apps/<uuid:app_id>/publish-histories",
            view_func=self.app_handler.get_publish_histories_with_page,
        )
        # 2.8 回退发布
        bp.add_url_rule(
            "/apps/<uuid:app_id>/fallback-history",
            methods=["POST"],
            view_func=self.app_handler.fallback_history_to_draft,
        )
        # 2.9 获取会话长期记忆
        bp.add_url_rule(
            "/apps/<uuid:app_id>/summary",
            view_func=self.app_handler.get_debug_conversation_summary,
        )
        # 2.10 更新会话长期记忆
        bp.add_url_rule(
            "/apps/<uuid:app_id>/summary",
            methods=["POST"],
            view_func=self.app_handler.update_debug_conversation_summary,
        )
        # 2.11 删除应用调试会话记录
        bp.add_url_rule(
            "/apps/<uuid:app_id>/conversations/delete-debug-conversation",
            methods=["POST"],
            view_func=self.app_handler.delete_debug_conversation,
        )

        # 2.12 调试会话
        bp.add_url_rule(
            "/apps/<uuid:app_id>/conversations",
            methods=["POST"],
            view_func=self.app_handler.debug_chat,
        )

        # 2.13 中断流式输出
        bp.add_url_rule(
            "/apps/<uuid:app_id>/conversations/tasks/<uuid:task_id>/stop",
            methods=["POST"],
            view_func=self.app_handler.stop_debug_chat,
        )

        # 2.14获取该应用的调试会话分页列表记录
        bp.add_url_rule(
            "/apps/<uuid:app_id>/conversations/messages",
            view_func=self.app_handler.get_debug_conversation_messages_with_page,
        )

        # 2.15获取指定应用的发布配置信息
        bp.add_url_rule(
            "/apps/<uuid:app_id>/published-config",
            view_func=self.app_handler.get_published_config,
        )
        # 2.16重新生成 WebApp 的凭证标识
        bp.add_url_rule(
            "/apps/<uuid:app_id>/published-config/regenerate-web-app-token",
            methods=["POST"],
            view_func=self.app_handler.regenerate_web_app_token,
        )

        # 3.1 内置插件广场模块
        bp.add_url_rule("/builtin-tools", view_func=self.builtin_tool_handler.get_builtin_tools)
        # 3.2 获取插件广场所有分类信息（不分页）
        bp.add_url_rule("/builtin-tools/categories", view_func=self.builtin_tool_handler.get_categories)
        # 3.3 获取icon
        bp.add_url_rule(
            "/builtin-tools/<string:provider_name>/icon",
            view_func=self.builtin_tool_handler.get_provider_icon,
        )
        # 3.4 获取某个服务商的工具
        bp.add_url_rule(
            "/builtin-tools/<string:provider_name>/tools/<string:tool_name>",
            view_func=self.builtin_tool_handler.get_provider_tool,
        )

        # 4.自定义API插件模块
        # 4.1 创建自定义api_tool
        bp.add_url_rule(
            "/api-tools",
            methods=["POST"],
            view_func=self.api_tool_handler.create_api_tool_provider,
        )
        # 4.2校验openapi_schema
        bp.add_url_rule(
            "/api-tools/validate-openapi-schema",
            methods=["POST"],
            view_func=self.api_tool_handler.validate_openapi_schema,
        )
        # 4.3获取工具列表
        bp.add_url_rule(
            "/api-tools",
            view_func=self.api_tool_handler.get_api_tool_providers_with_page,
        )
        # 4.4获取工具详情
        bp.add_url_rule(
            "/api-tools/<string:provider_id>",
            view_func=self.api_tool_handler.get_api_tool_provider,
        )
        # 4.5根据传递的provider_id+tool_name获取对应工具的参数详情信息
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>/tools/<string:tool_name>",
            view_func=self.api_tool_handler.get_api_tool,
        )
        # 4.6更新服务提供者信息
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>",
            methods=["POST"],
            view_func=self.api_tool_handler.update_api_tool_provider,
        )
        # 4.7删除服务提供商
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>/delete",
            methods=["POST"],
            view_func=self.api_tool_handler.delete_api_tool_provider,
        )

        # 5.上传文件模块
        bp.add_url_rule("/upload-files/file", methods=["POST"], view_func=self.upload_file_handler.upload_file)
        bp.add_url_rule("/upload-files/image", methods=["POST"], view_func=self.upload_file_handler.upload_image)

        # 6. 知识库模块
        # 6.1 创建知识库
        bp.add_url_rule("/datasets", methods=["POST"], view_func=self.dataset_handler.create_dataset)
        # 6.3 分页查询知识库
        bp.add_url_rule("/datasets", view_func=self.dataset_handler.get_datasets_with_page)
        # 6.3 查询知识库详情
        bp.add_url_rule("/datasets/<uuid:dataset_id>", view_func=self.dataset_handler.get_dataset)
        # 6.4 更新知识库
        bp.add_url_rule("/datasets/<uuid:dataset_id>", methods=["POST"], view_func=self.dataset_handler.update_dataset)
        # 6.5 获取指定知识库最近的查询列表
        bp.add_url_rule("/datasets/<uuid:dataset_id>/queries", view_func=self.dataset_handler.get_dataset_queries)
        # 6.6 删除数据库❌ -> TODO这接口有问题，报错subject table for an INSERT, UPDATE or DELETE expected, got <Dataset dcaf5254-6ebe-4fae-9d95-38a3d3a27b9c>.
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/delete",
            methods=["POST"],
            view_func=self.dataset_handler.delete_dataset,
        )

        # 7. 知识库文档模块
        # 7.1 创建文档
        bp.add_url_rule("/datasets/<uuid:dataset_id>/documents", methods=["POST"],
                        view_func=self.document_handler.create_documents)
        # 7.2获取指定知识库的文档列表
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents",
            view_func=self.document_handler.get_documents_with_page,
        )
        # 7.3获取指定文档基础信息
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>",
            view_func=self.document_handler.get_document,
        )
        # 7.4更新文档名称
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/name",
            methods=["POST"],
            view_func=self.document_handler.update_document_name,
        )
        # 7.5 更新文档开启状态
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/enabled",
            methods=["POST"],
            view_func=self.document_handler.update_document_enabled,
        )
        # 7.6 删除文档
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/delete",
            methods=["POST"],
            view_func=self.document_handler.delete_document,
        )
        # 7.7根据批处理标识获取处理进度
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/batch/<string:batch>",
            view_func=self.document_handler.get_documents_status,
        )

        # 8.文档片段模块
        # 8.1 获取指定文档的片段列表
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments",
            view_func=self.segment_handler.get_segments_with_page,
        )
        # 8.2新增文档片段信息
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments",
            methods=["POST"],
            view_func=self.segment_handler.create_segment,
        )
        # 8.3查询文档片段信息
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>",
            view_func=self.segment_handler.get_segment,
        )
        # 8.4更新文档片段信息
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>",
            methods=["POST"],
            view_func=self.segment_handler.update_segment,
        )
        # 8.5更新文档片段
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>",
            methods=["POST"],
            view_func=self.segment_handler.update_segment,
        )
        # 8.6更新文档片段开启状态
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>/enabled",
            methods=["POST"],
            view_func=self.segment_handler.update_segment_enabled,
        )
        # 8.7删除文档片段
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>/delete",
            methods=["POST"],
            view_func=self.segment_handler.delete_segment,
        )

        # 9.1指定知识库进行召回测试
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/hit",
            methods=["POST"],
            view_func=self.dataset_handler.hit,
        )

        # 10.授权认证模块
        # 10.1获取服务提供商跳转链接
        bp.add_url_rule("/oauth/<string:provider_name>", view_func=self.oauth_handler.provider)
        # 10.2根据传递的提供商名字+code获取第三方授权信息
        bp.add_url_rule(
            "/oauth/authorize/<string:provider_name>",
            methods=["POST"],
            view_func=self.oauth_handler.authorize,
        )
        # 10.3密码登录
        bp.add_url_rule(
            "/auth/password-login",
            methods=["POST"],
            view_func=self.auth_handler.password_login,
        )
        # 10.4退出登录
        bp.add_url_rule(
            "/auth/logout",
            methods=["POST"],
            view_func=self.auth_handler.logout,
        )

        # 11.1 账号设置模块
        bp.add_url_rule("/account", view_func=self.account_handler.get_current_user)
        # 11.2 更新密码
        bp.add_url_rule("/account/password", methods=["POST"], view_func=self.account_handler.update_password)
        bp.add_url_rule("/account/name", methods=["POST"], view_func=self.account_handler.update_name)
        bp.add_url_rule("/account/avatar", methods=["POST"], view_func=self.account_handler.update_avatar)

        # 12.1 AI辅助模块
        bp.add_url_rule("/ai/optimize-prompt", methods=["POST"], view_func=self.ai_handler.optimize_prompt)
        bp.add_url_rule(
            "/ai/suggested-questions", methods=["POST"],
            view_func=self.ai_handler.generate_suggested_questions,
        )

        # 13.1获取秘钥列表
        bp.add_url_rule("/openapi/api-keys", view_func=self.api_key_handler.get_api_keys_with_page)

        # 13.2创建API秘钥
        bp.add_url_rule(
            "/openapi/api-keys",
            methods=["POST"],
            view_func=self.api_key_handler.create_api_key,
        )

        # 13.3更新api_key开启状态
        bp.add_url_rule(
            "/openapi/api-keys/<uuid:api_key_id>/is-active",
            methods=["POST"],
            view_func=self.api_key_handler.update_api_key_is_active,
        )
        # 13.4删除api_key
        bp.add_url_rule(
            "/openapi/api-keys/<uuid:api_key_id>/delete",
            methods=["POST"],
            view_func=self.api_key_handler.delete_api_key,
        )
        bp.add_url_rule(
            "/openapi/api-keys/<uuid:api_key_id>",
            methods=["POST"],
            view_func=self.api_key_handler.update_api_key,
        )

        # 14.内置应用模块
        # 14.1 内置应用模块
        bp.add_url_rule("/builtin-apps/categories", view_func=self.builtin_app_handler.get_builtin_app_categories)
        # 14.2获取所有内置应用列表信息
        bp.add_url_rule("/builtin-apps", view_func=self.builtin_app_handler.get_builtin_apps)
        # 14.3将指定的内置应用添加到个人空间
        bp.add_url_rule(
            "/builtin-apps/add-builtin-app-to-space",
            methods=["POST"],
            view_func=self.builtin_app_handler.add_builtin_app_to_space,
        )

        # 14工作流模块
        # 14.获取所有工作流
        bp.add_url_rule("/workflows", view_func=self.workflow_handler.get_workflows_with_page)
        # 14.1创建工作流
        bp.add_url_rule("/workflows", methods=["POST"], view_func=self.workflow_handler.create_workflow)
        # 14.2获取工作流详情
        bp.add_url_rule("/workflows/<uuid:workflow_id>", view_func=self.workflow_handler.get_workflow)
        # 14.3更新工作流
        bp.add_url_rule(
            "/workflows/<uuid:workflow_id>",
            methods=["POST"],
            view_func=self.workflow_handler.update_workflow,
        )
        # 14.4删除工作流
        bp.add_url_rule(
            "/workflows/<uuid:workflow_id>/delete",
            methods=["POST"],
            view_func=self.workflow_handler.delete_workflow,
        )
        # 14.5更新工作流
        bp.add_url_rule(
            "/workflows/<uuid:workflow_id>/draft-graph",
            methods=["POST"],
            view_func=self.workflow_handler.update_draft_graph,
        )
        # 14.6获取工作流
        bp.add_url_rule(
            "/workflows/<uuid:workflow_id>/draft-graph",
            view_func=self.workflow_handler.get_draft_graph,
        )
        # 14.7发布工作流
        bp.add_url_rule(
            "/workflows/<uuid:workflow_id>/publish",
            methods=["POST"],
            view_func=self.workflow_handler.publish_workflow,
        )
        # 14.8取消发布工作流
        bp.add_url_rule(
            "/workflows/<uuid:workflow_id>/cancel-publish",
            methods=["POST"],
            view_func=self.workflow_handler.cancel_publish_workflow,
        )
        # 14.9调试
        bp.add_url_rule(
            "/workflows/<uuid:workflow_id>/debug",
            methods=["POST"],
            view_func=self.workflow_handler.debug_workflow,
        )

        # 15.语言模型模块
        # 15.1获取所有内置的语言模型
        bp.add_url_rule("/language-models", view_func=self.language_model_handler.get_language_models)
        # 15.2获取语言模型提供商的icon
        bp.add_url_rule(
            "/language-models/<string:provider_name>/icon",
            view_func=self.language_model_handler.get_language_model_icon,
        )
        # 15.3获取语言模型详情
        bp.add_url_rule(
            "/language-models/<string:provider_name>/<string:model_name>",
            view_func=self.language_model_handler.get_language_model,
        )

        # 13.辅助Agent模块
        bp.add_url_rule(
            "/assistant-agent/chat",
            methods=["POST"],
            view_func=self.assistant_agent_handler.assistant_agent_chat,
        )
        bp.add_url_rule(
            "/assistant-agent/chat/<uuid:task_id>/stop",
            methods=["POST"],
            view_func=self.assistant_agent_handler.stop_assistant_agent_chat,
        )
        bp.add_url_rule(
            "/assistant-agent/messages",
            view_func=self.assistant_agent_handler.get_assistant_agent_messages_with_page,
        )
        bp.add_url_rule(
            "/assistant-agent/delete-conversation",
            methods=["POST"],
            view_func=self.assistant_agent_handler.delete_assistant_agent_conversation,
        )

        # 14.应用统计模块
        bp.add_url_rule(
            "/analysis/<uuid:app_id>",
            view_func=self.analysis_handler.get_app_analysis,
        )

        # 15.WebApp模块
        bp.add_url_rule("/web-apps/<string:token>", view_func=self.web_app_handler.get_web_app)
        bp.add_url_rule(
            "/web-apps/<string:token>/chat",
            methods=["POST"],
            view_func=self.web_app_handler.web_app_chat,
        )
        bp.add_url_rule(
            "/web-apps/<string:token>/chat/<uuid:task_id>/stop",
            methods=["POST"],
            view_func=self.web_app_handler.stop_web_app_chat,
        )
        bp.add_url_rule("/web-apps/<string:token>/conversations", view_func=self.web_app_handler.get_conversations)

        openapi_bp.add_url_rule("/openapi/chat", methods=["post"], view_func=self.openapi_handler.chat)

        bp.add_url_rule('/ping', view_func=self.app_handler.ping)

        # 16.会话模块
        bp.add_url_rule(
            "/conversations/<uuid:conversation_id>/messages",
            view_func=self.conversation_handler.get_conversation_messages_with_page,
        )
        # bp.add_url_rule(
        #     "/conversations/<uuid:conversation_id>/delete",
        #     methods=["POST"],
        #     view_func=self.conversation_handler.delete_conversation,
        # )
        # bp.add_url_rule(
        #     "/conversations/<uuid:conversation_id>/messages/<uuid:message_id>/delete",
        #     methods=["POST"],
        #     view_func=self.conversation_handler.delete_message,
        # )
        bp.add_url_rule(
            "/conversations/<uuid:conversation_id>/name",
            view_func=self.conversation_handler.get_conversation_name,
        )
        bp.add_url_rule(
            "/conversations/<uuid:conversation_id>/name",
            methods=["POST"],
            view_func=self.conversation_handler.update_conversation_name,
        )
        # bp.add_url_rule(
        #     "/conversations/<uuid:conversation_id>/is-pinned",
        #     methods=["POST"],
        #     view_func=self.conversation_handler.update_conversation_is_pinned,
        # )

        # 6. 在应用上注册蓝图
        app.register_blueprint(bp)
        app.register_blueprint(openapi_bp)
