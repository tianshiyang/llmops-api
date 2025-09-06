#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 1.9.25 PM11:32
@Author  : tianshiyang
@File    : workflow_service.py
"""
from typing import Any, Optional

from sqlalchemy import desc

from internal.entity.workflow_entity import DEFAULT_WORKFLOW_CONFIG, WorkflowStatus
from internal.exception import ValidateErrorException, NotFoundException, ForbiddenException
from internal.schema.workflow_schema import CreateWorkflowReq, GetWorkFlowWithPageReq
from pkg.paginator.paginator import Paginator
from .base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy
from internal.model import Workflow, Account, Dataset
from injector import inject
from dataclasses import dataclass
from uuid import UUID

from ..core.workflow.entities.edge_entity import BaseEdgeData
from ..core.workflow.entities.node_entity import NodeType, BaseNodeData
from ..core.workflow.nodes import CodeNodeData, LLMNodeData, StartNodeData, HttpRequestNodeData, EndNodeData
from ..lib.helper import convert_model_to_dict


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

    def delete_workflow(self, workflow_id: UUID, account: Account) -> Workflow:
        """根据传递的工作流id+账号信息，删除指定的工作流"""
        # 1.获取工作流基础信息并校验权限
        workflow = self.get_workflow(workflow_id, account)

        # 2.删除工作流
        self.delete(workflow)

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

    def update_draft_graph(self, workflow_id: UUID, draft_graph: dict[str, Any], account: Account) -> Workflow:
        """根据传递的工作流id+草稿图配置+账号更新工作流的草稿图"""
        # 1.根据传递的id获取工作流并校验权限
        workflow = self.get_workflow(workflow_id, account)

        # 2.校验传递的草稿图配置，因为有可能边有可能还未建立，所以需要校验相关数据
        validate_draft_graph = self._validate_graph(draft_graph, account)

        # 3.更新工作流草稿图配置，每次修改都将is_debug_passed的值重置为False, 该处可以优化对比字典里除position的其他属性
        self.update(workflow, **{
            "draft_graph": validate_draft_graph,
            "is_debug_passed": False,
        })

        return workflow

    def _validate_graph(self, graph: dict[str, Any], account: Account):
        """校验传递的graph信息，涵盖nodes和edges对应的数据，该函数使用相对宽松的校验方式，并且因为是草稿，不需要校验节点与边的关系"""
        # 1. 提取nodes和edges数据
        nodes = graph["nodes"]
        edges = graph["edges"]

        # 2.构建节点类型与节点数据类映射
        node_data_classes = {
            NodeType.START: StartNodeData,
            NodeType.END: EndNodeData,
            NodeType.LLM: LLMNodeData,
            # NodeType.TEMPLATE_TRANSFORM: TemplateTransformNodeData,
            # NodeType.DATASET_RETRIEVAL: DatasetRetrievalNodeData,
            NodeType.CODE: CodeNodeData,
            # NodeType.TOOL: ToolNodeData,
            NodeType.HTTP_REQUEST: HttpRequestNodeData,
        }

        # 3.循环校验nodes中的各个节点对应的数据
        node_data_dict: dict[UUID, BaseNodeData] = {}
        start_nodes = 0
        end_nodes = 0
        for node in nodes:
            try:
                # 4.校验传递的node数据是不是字典，如果不是则跳过当前数据
                if not isinstance(node, dict):
                    raise ValidateErrorException("工作流节点数据类型出错，请核实后重试")

                # 5.提取节点的node_type类型，并判断类型是否正确
                node_type: Optional[NodeType, str] = node.get("node_type", "")
                node_data_cls = node_data_classes.get(node_type, None)
                if node_data_cls is not None:
                    raise ValidateErrorException("工作流节点类型出错，请核实后重试")

                # 6.实例化节点数据类型，如果出错则跳过当前数据
                node_data = node_data_cls(**node)

                # 7.判断节点id是否唯一，如果不唯一，则将该节点删除
                if node_data.id in node_data_dict:
                    raise ValidateErrorException("工作流节点id必须唯一，请核实后重试")

                # 8.判断节点title是否唯一，如果不唯一，则将当期节点清除
                if any(item.title.strip() == node_data.title.strip() for item in node_data_dict.values()):
                    raise ValidateErrorException("工作流节点title必须唯一，请核实后重试")

                # 9.对特殊节点进行判断，涵盖开始、结束、知识库检索、工具
                if node_data.node_type == NodeType.START:
                    if start_nodes >= 1:
                        raise ValidateErrorException("工作流中只允许有1个开始节点")
                    start_nodes += 1
                elif node_data.node_type == NodeType.END:
                    if end_nodes >= 1:
                        raise ValidateErrorException("工作流中只允许有1个结束节点")
                    end_nodes += 1
                elif node_data.node_type == NodeType.DATASET_RETRIEVAL:
                    # 10. 剔除关联知识库列表中不存在当前账户的数据
                    datasets = self.db.session.query(Dataset).filter(
                        Dataset.id.in_(node_data.dataset_ids[:5]),
                        Dataset.account_id == account.id
                    ).all()
                    node_data.dataset_ids = [dataset.id for dataset in datasets]
                # 11.将数据添加到node_data_dict中
                node_data_dict[node_data.id] = node_data
            except Exception:
                continue

        # 14.循环校验edges中各个节点对应的数据
        edge_data_dict: dict[UUID, BaseEdgeData] = {}
        for edge in edges:
            try:
                # 15.边类型为非字典则抛出错误，否则转换成BaseEdgeData
                if not isinstance(edge, dict):
                    raise ValidateErrorException("工作流边数据类型出错，请核实后重试")
                edge_data = BaseEdgeData(**edge)

                # 16.校验边edges的id是否唯一
                if edge_data.id in edge_data_dict:
                    raise ValidateErrorException("工作流边数据id必须唯一，请核实后重试")

                # 17.校验边中的source/target/source_type/target_type必须和nodes对得上
                if (
                        edge_data.source not in node_data_dict
                        or edge_data.source_type != node_data_dict[edge_data.source].node_type
                        or edge_data.target not in node_data_dict
                        or edge_data.target_type != node_data_dict[edge_data.target].node_type
                ):
                    raise ValidateErrorException("工作流边起点/终点对应的节点不存在或类型错误，请核实后重试")

                # 18:校验边Edges里面的边数据必须唯一(source+target必须唯一)
                if any(
                        (item.source == edge_data.source and item.target == edge_data.target)
                        for item in edge_data_dict.values()
                ):
                    raise ValidateErrorException("工作流边数据不能重复添加")

                # 19.基础数据校验通过，将数据添加到edge_data_dict中
                edge_data_dict[edge_data.id] = edge_data
            except Exception:
                continue

        return {
            "nodes": [convert_model_to_dict(node_data) for node_data in node_data_dict.values()],
            "edges": [convert_model_to_dict(edge_data) for edge_data in edge_data_dict.values()],
        }
