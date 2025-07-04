#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.7.25 PM11:49
@Author  : tianshiyang
@File    : document_schema.py
"""
import uuid

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, AnyOf, ValidationError

from internal.entity.dataset_entity import ProcessType, DEFAULT_PROCESS_RULE
from internal.schema import ListField, DictField


class CreateDocumentReq(FlaskForm):
    """创建/新增文档列表请求"""
    upload_file_ids = ListField("upload_file_ids")
    process_type = StringField("process_type", validators=[
        DataRequired("文档处理类型不能为空"),
        AnyOf(values=[ProcessType.CUSTOM, ProcessType.AUTOMATIC], message="处理类型格式错误")
    ])
    rule = DictField("rule")

    def validate_upload_file_ids(self, field: ListField) -> None:
        """校验上传id列表"""
        if not isinstance(field.data, list):
            raise ValidationError("文件id列表格式必须是数组")

        if len(field.data) == 0 or len(field.data) > 10:
            raise ValidationError("新增文档数范围在0-10")

        for upload_file_id in field.data:
            try:
                uuid.UUID(upload_file_id)
            except Exception as e:
                raise ValidationError("文件id的格式必须是uuid")

        # 删除重复数据并更新
        field.data = list(dict.fromkeys(field.data))

    def validate_rule(self, field: DictField) -> None:
        """校验上传处理规则"""
        # 1.校验处理模式，如果为自动，则为rule附默认值
        if self.process_type.data == ProcessType.AUTOMATIC:
            field.data = DEFAULT_PROCESS_RULE["rule"]
        else:
            # 2.检测自定义处理类型下是否传递了rule
            if not isinstance(field.data, dict) or len(field.data) == 0:
                raise ValidationError("自定义处理模式下，rule不能为空")
            # 3.校验pre_process_rules涵盖：非空、列表类型
            if "pre_process_rules" not in field.data or not isinstance(field.data["pre_process_rules"], list):
                raise ValidationError("pre_process_rules必须为列表")
            # 4.提取pre_process_rules中唯一的处理规则，避免重复处理
            unique_pre_process_rule_dict = {}
            for pre_process_rule in field.data["pre_process_rules"]:
                # 5.校验id参数，非空，id规范
                if "id" not in pre_process_rule or pre_process_rule['id'] not in ["remove_extra_space",
                                                                                  "remove_url_and_email"]:
                    raise ValidationError("预处理id格式错误")
                # 6.校验enabled参数，涵盖：非空，布尔值
                if "enabled" not in pre_process_rule or not isinstance(pre_process_rule["enabled"], bool):
                    raise ValidationError("预处理enabled格式错误")
                # 7.将数据添加到唯一字典中，过滤无关数据
                unique_pre_process_rule_dict[pre_process_rule["id"]] = {
                    "id": pre_process_rule["id"],
                    "enabled": pre_process_rule["enabled"],
                }
            # 8.判断一下是否传递了两个处理规则
            if len(unique_pre_process_rule_dict) != 2:
                raise ValidationError("预处理规则格式错误，请重新尝试")
            # 9.将处理后的数据转换成列表并覆盖处理规则
            field.data["pre_process_rules"] = list(unique_pre_process_rule_dict.values())

            # 10.校验分段参数segment, 覆盖：非空、字典
            if "segment" not in field.data or not isinstance(field.data["segment"], dict):
                raise ValidationError('分段设置不能为空且为字典')
            # 11.校验分隔符separators，涵盖：非空、列表、子元素为字符串
            if "separators" not in field.data["segment"] or not isinstance(field.data["separators"], list):
                raise ValidationError("分割符列表不能为空且为列表")
            for separator in field.data["segment"]["separators"]:
                if not isinstance(separator, str):
                    raise ValidationError("分隔符列表元素类型错误")
            if len(field.data["segment"]["separators"]) == 0:
                raise ValidationError("分隔符列表不能为空列表")
            
            # 12.校验分块大小chunk_size，涵盖了：非空、数字、范围
            if "chunk_size" not in field.data["segment"] or not isinstance(field.data["segment"]["chunk_size"],
                                                                           int):
                raise ValidationError("分割块大小不能为空且为整数")
            if field.data["segment"]["chunk_size"] < 100 or field.data["segment"]["chunk_size"] > 1000:
                raise ValidationError("分割块大小在100-1000")

            # 13.校验块重叠大小chunk_overlap，涵盖：非空、数字、范围
            if (
                    "chunk_overlap" not in field.data["segment"]
                    or not isinstance(field.data["segment"]["chunk_overlap"], int)
            ):
                raise ValidationError("块重叠大小不能为空且为整数")
            if not (0 <= field.data["segment"]["chunk_overlap"] <= field.data["segment"]["chunk_size"] * 0.5):
                raise ValidationError(f"块重叠大小在0-{int(field.data['segment']['chunk_size'] * 0.5)}")
            # 14.更新并提出多余数据
            field.data = {
                "pre_process_rules": field.data["pre_process_rules"],
                "segment": {
                    "separators": field.data["segment"]["separators"],
                    "chunk_size": field.data["segment"]["chunk_size"],
                    "chunk_overlap": field.data["segment"]["chunk_overlap"],
                }
            }
