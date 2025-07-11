#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 22.6.25 PM7:29
@Author  : tianshiyang
@File    : paginator.py
"""
import math
from dataclasses import dataclass
from typing import Any

from flask_wtf import FlaskForm
from wtforms.fields.numeric import IntegerField
from wtforms.validators import NumberRange, Optional

from pkg.sqlalchemy import SQLAlchemy


class PaginatorReq(FlaskForm):
    current_page: int = IntegerField("current_page", default=1, validators=[
        Optional(),
        NumberRange(min=1, max=9999, message="当前页数的范围在1-9999")
    ])
    page_size: int = IntegerField("page_size", default=20, validators=[
        Optional(),
        NumberRange(min=1, max=50, message="每页数据的条数范围在1-50")
    ])


@dataclass
class Paginator:
    # 分页器
    total_page: int = 0  # 总页数
    total_record: int = 0  # 总条数
    current_page: int = 1  # 当前页数
    page_size: int = 20  # 每页条数

    def __init__(self, db: SQLAlchemy, req: PaginatorReq = None):
        if req is not None:
            self.page_size = req.page_size.data
            self.current_page = req.current_page.data
        self.db = db

    def paginate(self, select):
        """对传入的查询进行分页"""
        # 1.调用db.paginate进行数据分页
        p = self.db.paginate(select, page=self.current_page, per_page=self.page_size, error_out=False)
        self.total_record = p.total
        self.total_page = math.ceil(p.total / self.page_size)
        print("total_record", self.total_record)
        print("total_page", self.total_page)
        # 3.返回分页后的数据
        return p.items


@dataclass
class PageModel:
    list: list[Any]
    paginator: Paginator
