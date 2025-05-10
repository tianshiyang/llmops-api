# #!/user/bin/env python
# # -*- coding: utf-8 -*-
# """
# @Time    : 2025/4/19 22:35
# @Author  : 1685821150@qq.com
# @File    : test_app_handler.py
# """
# import pytest
#
# from pkg import HttpCode
#
#
# class TestAppHandler:
#     @pytest.mark.parametrize("query", [None, "你好，你是谁?"])
#     def test_completion(self, query, client):
#         resp = client.post("/app/completion", json={"query": query})
#         assert resp.status_code == 200
#         if query is None:
#             assert resp.json.get("code") == HttpCode.VALIDATE_ERROR
#         else:
#             assert resp.json.get("code") == HttpCode.SUCCESS
