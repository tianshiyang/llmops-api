#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 21.6.25 PM9:11
@Author  : tianshiyang
@File    : api_tool_service.py
"""
from dataclasses import dataclass

from injector import inject
from sqlalchemy import desc

from internal.core.tools.api_tools.openapi_schema import OpenAPISchema
from internal.exception import ValidateErrorException, NotFoundException
from internal.model import ApiToolProvider, ApiTool
from internal.schema.api_tool_schema import CreateApiToolReq, GetApiToolProvidersWithPageReq, UpdateApiToolProviderReq
import json

from internal.service.base_service import BaseService
from pkg.paginator.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class ApiToolService(BaseService):
    db: SQLAlchemy

    def create_api_tool(self, req: CreateApiToolReq) -> None:
        """根据传递的请求创建自定义API工具"""
        # todo:等待授权认证模块完成进行切换调整
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        # 1.检验并提取openapi_schema对应的数据
        openapi_schema = self.parse_openapi_schema(req.openapi_schema.data)

        # 2.查询当前登录的账号是否已经创建了同名的工具提供者，如果是则抛出错误
        api_tool_provider = self.db.session.query(ApiToolProvider).filter_by(
            account_id=account_id,
            name=req.name.data,
        ).one_or_none()

        if api_tool_provider:
            raise ValidateErrorException(f"该工具提供者名字{req.name}已存在")

        # 3.首先创建工具提供者，并获取工具提供者的id信息，然后在创建工具信息
        api_tool_provider = self.create(
            ApiToolProvider,
            account_id=account_id,
            name=req.name.data,
            icon=req.icon.data,
            description=openapi_schema.description,
            openapi_schema=req.openapi_schema.data,
            headers=req.headers.data,
        )

        # 4.创建api工具并关联api_tool_provider
        for path, path_item in openapi_schema.paths.items():
            for method, method_item in path_item.items():
                self.create(
                    ApiTool,
                    account_id=account_id,
                    provider_id=api_tool_provider.id,
                    name=method_item.get("operationId"),
                    description=method_item.get("description"),
                    url=f"{openapi_schema.server}{path}",
                    method=method,
                    parameters=method_item.get("parameters", []),
                )

    def get_api_tool_providers_with_page(self, req: GetApiToolProvidersWithPageReq):
        """获取自定义API工具服务提供者分页列表数据"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        paginator = Paginator(db=self.db, req=req)
        filters = [ApiToolProvider.account_id == account_id]
        if req.search_word.data:
            filters.append(ApiToolProvider.name.ilike(f"%{req.search_word.data}%"))

        api_tool_providers = paginator.paginate(
            self.db.session.query(ApiToolProvider).filter(*filters).order_by(desc("created_at")))

        return api_tool_providers, paginator

    def get_api_tool_provider(self, provider_id: str):
        """根据传递的provider_id获取工具提供者的原始信息"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        filters = [ApiToolProvider.account_id == account_id, ApiToolProvider.id == provider_id]
        result = self.db.session.query(ApiToolProvider).filter(*filters).one_or_none()
        if result is None or str(result.account_id) != account_id:
            raise NotFoundException("该工具提供者不存在")
        return result

    def get_api_tool(self, provider_id: str, tool_name: str) -> ApiTool:
        """根据传递的provider_id + tool_name获取对应工具的参数详情信息"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        api_tool = self.db.session.query(ApiTool).filter_by(provider_id=provider_id, name=tool_name).one_or_none()
        if api_tool is None or str(api_tool.account_id) != account_id:
            raise NotFoundException("该工具不存在")
        return api_tool

    def update_api_tool_provider(self, provider_id: str, req: UpdateApiToolProviderReq):
        """根据传递的provider_id+req更新对应的API工具提供者信息"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        # 1.根据传递的provider_id查找API工具提供者信息并校验
        api_tool_provider = self.get(ApiToolProvider, provider_id)
        if api_tool_provider is None or str(api_tool_provider.account_id) != account_id:
            raise ValidateErrorException("该工具提供者不存在")
        # 2.校验openapi_schema数据
        openapi_schema = self.parse_openapi_schema(req.openapi_schema.data)
        # 3.检测当前账号是否已经创建了同名的工具提供者，如果是则抛出错误
        check_api_tool_provider = self.db.session.query(ApiToolProvider).filter(
            ApiToolProvider.id != provider_id,
            ApiToolProvider.name == req.name.data,
            ApiToolProvider.account_id == api_tool_provider.account_id,
        ).one_or_none()
        if check_api_tool_provider:
            raise ValidateErrorException(f"该工具提供者名字{req.name.data}已存在")
        # 4.开启数据库的自动提交
        with self.db.auto_commit():
            # 5.先删除该工具提供者下的所有工具
            self.db.session.query(ApiTool).filter(
                ApiToolProvider.id == provider_id,
                ApiTool.account_id == account_id
            ).delete()
            # 6.修改工具提供者信息
        self.update(
            api_tool_provider,
            name=req.name.data,
            icon=req.icon.data,
            headers=req.headers.data,
            description=openapi_schema.description,
            openapi_schema=req.openapi_schema.data,
        )

        # 7.新增工具信息从而完成覆盖更新
        for path, path_item in openapi_schema.paths.items():
            for method, method_item in path_item.items():
                self.create(
                    ApiTool,
                    account_id=account_id,
                    provider_id=api_tool_provider.id,
                    name=method_item.get("operationId"),
                    description=method_item.get("description"),
                    url=f"{openapi_schema.server}{path}",
                    method=method,
                    parameters=method_item.get("parameters", []),
                )

    @classmethod
    def parse_openapi_schema(cls, openapi_schema_str: str) -> OpenAPISchema:
        """解析传递的openapi_schema字符串，如果出错则抛出错误"""
        try:
            data = json.loads(openapi_schema_str.strip())
            if not isinstance(data, dict):
                raise
        except Exception as e:
            raise ValidateErrorException("传递数据必须符合OpenAPI规范的JSON字符串")

        return OpenAPISchema(**data)
