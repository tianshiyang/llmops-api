#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.4.25 AM12:01
@Author  : 1685821150@qq.com
@File    : app.py
"""
import dotenv
from flask_cors import CORS

from pkg.sqlalchemy import SQLAlchemy
from injector import Injector

from app.http.moudle import ExtensionModule
from config import Config
from internal.router import Router
from internal.server import Http
from flask_migrate import Migrate

# 将env加载到环境中
dotenv.load_dotenv()

conf = Config()

# 加载配置
injector = Injector([ExtensionModule])

app = Http(
    __name__,
    router=injector.get(Router),
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    conf=conf,
)

celery = app.extensions["celery"]

# CORS(app, resources={
#     r"/*": {
#         "origins": "*",
#         "supports_credentials": True,
#         # "methods": ["GET", "POST"],
#         # "allow_headers": ["Content-Type"],
#     }
# })
if __name__ == '__main__':
    app.run(debug=True)
