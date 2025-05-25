#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM6:52
@Author  : tianshiyang
@File    : 2.Office文档加载器.py
"""
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, UnstructuredExcelLoader

pdf_loader = UnstructuredWordDocumentLoader("./喵喵.docx")
pdf_elements = pdf_loader.load()
# print(pdf_elements)
# print(len(pdf_elements))
# print(pdf_elements[0].metadata)

excel_loader = UnstructuredExcelLoader("./员工考勤表.xlsx", mode="elements")
excel_documents = excel_loader.load()

print(excel_documents)
print(len(excel_documents))
print(excel_documents[0].metadata)
