#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
create_elasticsearch_index.py
"""

import argparse
from elasticsearch import Elasticsearch
from db_config import get_elasticsearch_config

# 1. 设置命令行参数
parser = argparse.ArgumentParser(description="创建 Elasticsearch 索引")
parser.add_argument('--force', action='store_true', 
                    help='【危险】强制删除已存在的索引并重建，会清空所有数据！')
args = parser.parse_args()

es_config = get_elasticsearch_config()

es = Elasticsearch(
    [f"{es_config.get('scheme', 'http')}://{es_config['host']}:{es_config['port']}"],
    basic_auth=(es_config['username'], es_config['password']),
    verify_certs=False
)

index_name = "reits_announcements"

# 为与数据库 text_segmentation_embedding 对应，这里列出相应字段
index_body = {
    "mappings": {
        "properties": {
            "id": {"type": "long"},
            "global_id": {"type": "keyword"},
            "chunk_id": {"type": "long"},
            "file_path": {"type": "keyword"},
            "date": {"type": "date"},   # 需保证插入时是 'yyyy-MM-dd' 或类似
            "fund_code": {"type": "keyword"},
            "short_name": {"type": "text"},
            "announcement_title": {"type": "text"},
            "doc_type_1": {"type": "keyword"},
            "doc_type_2": {"type": "keyword"},
            "announcement_link": {"type": "keyword"},
            "source_file": {"type": "keyword"},
            "page_num": {"type": "keyword"},
            "picture_path": {"type": "keyword"},
            "char_count": {"type": "integer"},
            "prev_chunks": {"type": "keyword"},
            "next_chunks": {"type": "keyword"},
            "text": {"type": "text"} 
            # 不存 embedding 到 ES, 由 Milvus 做向量检索
        }
    }
}

# 2. 加入安全机制判断
if es.indices.exists(index=index_name):
    if args.force:
        print(f"⚠️ 检测到 --force 参数，正在强制删除已存在的索引: {index_name}...")
        es.indices.delete(index=index_name)
        print(f"已删除索引: {index_name}")
    else:
        print(f"⏭️ 索引 '{index_name}' 已存在。为了保护数据，未做任何操作。")
        print("👉 如果你确实想重建（会清空数据），请加上 --force 参数运行。")
        exit(0)  # 安全退出，不执行后面的创建逻辑

# 3. 创建新索引（只有在不存在，或者 force 被触发后才会走到这里）
es.indices.create(index=index_name, body=index_body)
print(f"✅ 索引 '{index_name}' 创建成功！")
