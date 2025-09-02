#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 1.9.25 PM11:32
@Author  : tianshiyang
@File    : workflow_service.py
"""
from pip._internal import req
from sqlalchemy import desc

from internal.core.workflow.entities.workflow_entity import DEFAULT_WORKFLOW_CONFIG, WorkflowStatus
from internal.exception import ValidateErrorException, NotFoundException, ForbiddenException
from internal.schema.workflow_schema import CreateWorkflowReq, UpdateWorkflowReq, GetWorkFlowWithPageReq
from pkg.paginator.paginator import Paginator
from .base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy
from internal.model import Workflow, Account
from injector import inject
from dataclasses import dataclass
from uuid import UUID


@inject
@dataclass
class WorkflowService(BaseService):
    db: SQLAlchemy

    def create_workflow(self, req: CreateWorkflowReq, account: Account) -> Workflow:
        """根据传递的请求信息创建工作流"""
        # 1.根据传递的工作流名称查询工作流信息
        check_workflow = self.db.session.query(Workflow).filter(
            Workflow.account_id == account.id,
            Workflow.tool_call_name == req.tool_call_name.data.strip()
        ).one_or_none()
        if check_workflow:
            raise ValidateErrorException(f"在当前账号下已创建[{req.tool_call_name.data}]工作流，不支持重名")

        # 2.调用数据库服务创建工作流
        return self.create(Workflow, **{
            **req.data,
            **DEFAULT_WORKFLOW_CONFIG,
            "account_id": account.id,
            "is_debug_passed": False,
            "status": WorkflowStatus.DRAFT.value,
            "tool_call_name": req.tool_call_name.data.strip()
        })

    def get_workflow(self, workflow_id: UUID, account: Account) -> Workflow:
        """根据传递的工作流id，获取指定的工作流基础信息"""
        # 1.查询数据库获取工作流基础信息
        workflow = self.get(Workflow, workflow_id)

        # 2.判断工作流是否存在
        if not workflow:
            raise NotFoundException("该工作流不存在，请核实后重试")

        # 3.判断当前账号时候有权限访问该应用
        if workflow.account_id != account.id:
            raise ForbiddenException("当前账号无权限访问该应用，请核实后尝试")

        return workflow

    def update_workflow(self, workflow_id: UUID, account: Account, **kwargs) -> Workflow:
        """根据传递的工作流id+请求更新工作流基础信息"""
        # 1.获取工作流基础信息并校验权限
        workflow = self.get_workflow(workflow_id, account)

        # 2.根据传递的工具调用名称查询是否存在重命名工作流
        check_workflow = self.db.session.query(Workflow).filter(
            Workflow.tool_call_name == kwargs.get("tool_call_name", "").strip(),
            Workflow.account_id == account.id,
            Workflow.id != workflow_id
        ).one_or_none()
        if check_workflow:
            raise ValidateErrorException(f"在当前账号下已创建[{kwargs.get('tool_call_name', '')}]工作流，不支持重名")

        # 更新工作流基础信息
        self.update(workflow, **kwargs)
        return workflow

    def GetWorkFlowWithPageReq(self, req: GetWorkFlowWithPageReq, account: Account) -> tuple[list[Workflow], Paginator]:
        """根据传递的信息获取工作流分页列表数据"""
        # 1. 构建分页器
        paginator = Paginator(db=self.db, req=req)

        # 2.构建查询
        filters = [Workflow.account_id == account.id]
        if req.search_word.data:
            filters.append(Workflow.name.ilike(f"%{req.search_word.data}%"))
        if req.status.data:
            filters.append(Workflow.status == req.status.data)

        # 3.分页查询数据
        workflows = paginator.paginate(
            self.db.session.query(Workflow).filter(*filters).order_by(desc("created_at"))
        )

        return workflows, paginator
