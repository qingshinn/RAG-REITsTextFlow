# from mineru.parser import MinerUApiParser

# # 初始化解析器，指向你本地运行的 MinerU 服务
# parser = MinerUApiParser(
#     api_url="http://127.0.0.1:8000",  # 注意：这是 /v1 之前的服务根地址
#     tier="standard",                  # CPU 环境推荐 standard
#     include_images=True               # 是否包含解析出的图片
# )

# # 同步解析 PDF
# result = parser.parse("test.pdf", page_range="1-2")  # page_range 可选，从1开始计

# # 获取 Markdown 和 JSON 结果
# markdown_content = result.markdown()
# json_content = result.to_json()

# print(markdown_content[:5000])

# print("="*50)

# print(json_content)


# #扫描页跨页表格检测
# import os
# import cv2
# import torch
# import json
# import base64
# import shutil
# import logging
# import numpy as np
# from PIL import Image
# from openai import OpenAI
# from transformers import TableTransformerForObjectDetection
# import torchvision.transforms as transforms
# import re
# from builtins import open
# from step3_cross_page_table_detector import CrossPageTableDetector
# from model_config import MODEL_CONFIG
# from file_paths_config import OUTPUT_DIR, table_transformer_path  # 从配置文件中导入文件路径配置
# import pytesseract  # [新增] 用于检测文字方向
# from pytesseract import TesseractError
# import pymysql
# from db_config import get_db_announcement_config  # 新增数据库配置导入


from mineru import MinerU

# 方式一：直接解析在线文件 URL
client = MinerU()
result = client.flash_extract("https://cdn-mineru.openxlab.org.cn/demo/example.pdf")
print(result.markdown)

# 方式二：解析本地文件（≤10MB，≤20页）
# result = client.flash_extract("test.pdf")
# print(result.markdown)

# 方式三：解析本地图片
# result = client.flash_extract("你的文件.png")
# print(result.markdown)