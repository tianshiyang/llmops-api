#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 1.9.25 PM11:23
@Author  : tianshiyang
@File    : workflow_handler.py
"""
from flask_login import login_required, current_user
from injector import inject
from dataclasses import dataclass

from internal.schema.workflow_schema import CreateWorkflowReq
from internal.service.workflow_service import WorkflowService
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class WorkflowHandler:
    workflow_service: WorkflowService

    @login_required
    def create_workflow(self):
        req = CreateWorkflowReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务创建工作流
        workflow = self.workflow_service.create_workflow(req, current_user)
        return success_json({"id": workflow.id})
