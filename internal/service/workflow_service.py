#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 1.9.25 PM11:32
@Author  : tianshiyang
@File    : workflow_service.py
"""
from internal.core.workflow.entities.workflow_entity import DEFAULT_WORKFLOW_CONFIG, WorkflowStatus
from internal.exception import ValidateErrorException
from internal.schema.workflow_schema import CreateWorkflowReq
from .base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy
from internal.model import Workflow, Account
from injector import inject
from dataclasses import dataclass


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
