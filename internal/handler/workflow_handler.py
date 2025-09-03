#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 1.9.25 PM11:23
@Author  : tianshiyang
@File    : workflow_handler.py
"""
from flask import request
from flask_login import login_required, current_user
from injector import inject
from dataclasses import dataclass

from internal.schema.workflow_schema import CreateWorkflowReq, UpdateWorkflowReq, GetWorkflowResp, \
    GetWorkFlowWithPageReq, GetWorkflowsWithPageResp
from internal.service.workflow_service import WorkflowService
from pkg.paginator.paginator import PageModel
from pkg.response import validate_error_json, success_json, success_message
from uuid import UUID


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

    @login_required
    def delete_workflow(self, workflow_id: UUID):
        """根据传递的工作流id删除指定的工作流"""
        self.workflow_service.delete_workflow(workflow_id, current_user)
        return success_message("删除工作流成功")

    @login_required
    def get_workflow(self, workflow_id: UUID):
        """根据传递的工作流id获取工作流详情"""
        workflow = self.workflow_service.get_workflow(workflow_id, current_user)
        resp = GetWorkflowResp()
        return success_json(resp.dump(workflow))

    @login_required
    def get_workflows_with_page(self):
        """获取当前登录账号下的工作流分页列表数据"""
        req = GetWorkFlowWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 获取分页列表数据
        workflows, paginator = self.workflow_service.GetWorkFlowWithPageReq(req, current_user)

        # 构建响应
        reps = GetWorkflowsWithPageResp(many=True)
        return success_json(PageModel(list=reps.dump(workflows), paginator=paginator))

    @login_required
    def update_workflow(self, workflow_id: UUID):
        req = UpdateWorkflowReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.workflow_service.update_workflow(workflow_id, current_user, **req.data)
        return success_message("修改工作流基础信息成功")

    @login_required
    def update_draft_graph(self, workflow_id: UUID):
        """根据传递的工作流id+请求信息更新工作流草稿图配置"""
        # 1.提取草稿图接口请求json数据
        draft_graph_dict = request.get_json(force=True, silent=True) or {
            "nodes": [],
            "edges": [],
        }

        # 2.调用服务更新工作流的草稿图配置
        self.workflow_service.update_draft_graph(workflow_id, draft_graph_dict, current_user)

        return success_message("更新工作流草稿配置成功")
