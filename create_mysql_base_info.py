#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
create_mysql_base_info.py
在 reits 库中创建 `files_info` 表（原 `公告信息` 表）。
"""

import argparse  # 【新增】导入参数解析模块
import pymysql
from db_config import get_db_config

# 【新增】设置命令行参数
parser = argparse.ArgumentParser(description="创建 MySQL 数据表")
parser.add_argument('--force', action='store_true', 
                    help='【危险】强制删除已存在的表并重建，会清空所有数据！')
args = parser.parse_args()

TABLE_NAME = "files_info"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `announcement_title` VARCHAR(255) NOT NULL COMMENT '公告标题',
  `fund_code` VARCHAR(20) NOT NULL COMMENT '基金代码，如 123456.OF',
  `date` DATE NOT NULL COMMENT '公告日期',
  `doc_type_1` VARCHAR(50) DEFAULT NULL COMMENT '公告一级分类',
  `doc_type_2` VARCHAR(50) DEFAULT NULL COMMENT '公告二级分类',
  `announcement_link` VARCHAR(500) DEFAULT NULL COMMENT '原始公告链接',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_title_code_date` (`announcement_title`, `fund_code`, `date`),
  KEY `idx_fund_code` (`fund_code`),
  KEY `idx_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='REITs公告信息表';
"""


def create_table():
    conn = None
    try:
        db_conf = get_db_config()
        # 确保使用 utf8mb4，避免中文表名/字段名乱码
        db_conf.setdefault("charset", "utf8mb4")
        conn = pymysql.connect(**db_conf)
        
        with conn.cursor() as cursor:
            # 检查表是否存在
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
                    return  # 安全退出，不执行后面的建表逻辑
            
            # 创建表（只有表不存在，或者被 --force 删除后，才会走到这里）
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