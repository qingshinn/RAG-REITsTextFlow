#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
create_processed_files_table.py
在 announcement 库中创建 `processed_files` 表。
"""

import argparse  # 【新增】导入参数解析模块
import pymysql
from db_config import get_db_announcement_config

# 【新增】设置命令行参数
parser = argparse.ArgumentParser(description="创建 MySQL 数据表 (processed_files)")
parser.add_argument('--force', action='store_true', 
                    help='【危险】强制删除已存在的表并重建，会清空所有数据！')
args = parser.parse_args()

TABLE_NAME = "processed_files"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
  `file_name` VARCHAR(255) NOT NULL COMMENT 'PDF文件名，主键',
  `file_path` VARCHAR(500) NOT NULL COMMENT 'PDF完整路径',
  `date` DATE NOT NULL COMMENT '公告日期',
  `fund_code` VARCHAR(20) NOT NULL COMMENT '基金代码',
  `short_name` VARCHAR(100) DEFAULT NULL COMMENT '基金简称',
  `announcement_title` VARCHAR(255) DEFAULT NULL COMMENT '公告标题',
  `doc_type_1` VARCHAR(50) DEFAULT NULL COMMENT '公告一级类型',
  `doc_type_2` VARCHAR(50) DEFAULT NULL COMMENT '公告二级类型',
  `announcement_link` VARCHAR(500) DEFAULT NULL COMMENT '公告原始链接',
  `text_extracted` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '文本是否已提取',
  `table_detection_vector_done` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '表格检测向量是否完成',
  `table_detection_scan_done` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '表格检测扫描是否完成',
  `table_describe_done` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '表格描述是否完成',
  `not_table_describe_done` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '非表格描述是否完成',
  `merge_done` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '合并是否完成',
  `text_segmentation` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '文本分割是否完成',
  `embedding_done` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '向量化是否完成',
  `vector_database_done` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '向量数据库入库是否完成',
  `elasticsearch_database_done` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT 'ES入库是否完成',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`file_name`),
  KEY `idx_fund_code` (`fund_code`),
  KEY `idx_date` (`date`),
  KEY `idx_doc_type_1` (`doc_type_1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='PDF处理状态表';
"""


def create_table():
    conn = None
    try:
        db_conf = get_db_announcement_config()
        db_conf.setdefault("charset", "utf8mb4")
        conn = pymysql.connect(**db_conf)
        
        with conn.cursor() as cursor:
            # 【新增】检查表是否存在
            cursor.execute(f"SHOW TABLES LIKE '{TABLE_NAME}'")
            table_exists = cursor.fetchone()

            if table_exists:
                if args.force:
                    print(f"⚠️ 检测到 --force 参数，正在强制删除已存在的表: `{TABLE_NAME}` ...")
                    cursor.execute(f"DROP TABLE `{TABLE_NAME}`")
                    print(f"表 `{TABLE_NAME}` 已删除。")
                else:
                    print(f"⏭️ 表 `{TABLE_NAME}` 已存在。为了保护数据，未做任何操作。")
                    print(f"👉 如果你确实想重建（会清空数据），请加上 --force 参数运行。")
                    return  # 【新增】安全退出，不执行后面的建表逻辑

            # 【修改】只有表不存在，或者被 --force 删除后，才会走到这里
            print(f"正在创建表 `{TABLE_NAME}` ...")
            cursor.execute(CREATE_TABLE_SQL)
            print(f"✅ 表 `{TABLE_NAME}` 创建成功！")
            
        conn.commit()
        
    except Exception as e:
        print(f"创建表 `{TABLE_NAME}` 失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_table()