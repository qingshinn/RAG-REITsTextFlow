#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增量导入 Excel 中的公告基础信息到 files_info 表。

行为：
1. 使用 db_config.get_db_config() 读取数据库配置
2. 读取 Excel 文件
3. 与数据库中已有数据进行对比，过滤掉已存在的记录
4. 只插入新的记录
5. 记录日志
"""

import logging
import os
from typing import Iterable, List, Set, Tuple

import pandas as pd
import pymysql

from db_config import get_db_config
from file_paths_config import PDF_DIR

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(CURRENT_DIR, "log")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "base_info_import.log")
EXCEL_PATH = os.path.join(PDF_DIR, "files_info.xlsx")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def normalize_excel(df: pd.DataFrame) -> pd.DataFrame:
    """标准化 Excel 列名和字段格式."""
    # 兼容中文列名和英文列名
    rename_map = {
        "公告标题": "announcement_title",
        "标题": "announcement_title",
        "基金代码": "fund_code",
        "代码": "fund_code",
        "公告日期": "date",
        "日期": "date",
        "一级分类": "doc_type_1",
        "分类1": "doc_type_1",
        "二级分类": "doc_type_2",
        "分类2": "doc_type_2",
        "原始链接": "announcement_link",
        "链接": "announcement_link",
        "announcement_title": "announcement_title",
        "fund_code": "fund_code",
        "date": "date",
        "doc_type_1": "doc_type_1",
        "doc_type_2": "doc_type_2",
        "announcement_link": "announcement_link",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    required = ["announcement_title", "fund_code", "date"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Excel 缺少必要列: {missing}")

    df = df.copy()
    df["announcement_title"] = df["announcement_title"].fillna("").astype(str).str.strip()
    df["fund_code"] = df["fund_code"].fillna("").astype(str).str.strip()

    # 转成日期字符串，避免无效日期导致后续匹配失败
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"].notna()].copy()
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    if "doc_type_1" not in df.columns:
        df["doc_type_1"] = None
    if "doc_type_2" not in df.columns:
        df["doc_type_2"] = None
    if "announcement_link" not in df.columns:
        df["announcement_link"] = None

    df["doc_type_1"] = df["doc_type_1"].where(df["doc_type_1"].notna(), None)
    df["doc_type_2"] = df["doc_type_2"].where(df["doc_type_2"].notna(), None)
    df["announcement_link"] = df["announcement_link"].where(df["announcement_link"].notna(), None)

    df = df[
        df["announcement_title"].ne("")
        & df["fund_code"].ne("")
        & df["date"].ne("")
    ].copy()

    df = df.drop_duplicates(subset=["announcement_title", "fund_code", "date"], keep="last")
    return df


def fetch_db_keys() -> Set[Tuple[str, str, str]]:
    """查询数据库已存在的唯一键集合，避免重复插入."""
    db_conf = get_db_config()
    conn = pymysql.connect(**db_conf)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT announcement_title, fund_code, date FROM files_info"
            )
            rows = cursor.fetchall()
        return {
            (str(title).strip(), str(fund_code).strip(), str(date_value))
            for title, fund_code, date_value in rows
        }
    except Exception as exc:
        logger.exception("读取数据库现有 files_info 记录失败: %s", exc)
        raise
    finally:
        conn.close()


def get_new_rows(df: pd.DataFrame, db_keys: Set[Tuple[str, str, str]]) -> List[dict]:
    """筛选出数据库中不存在的新增记录."""
    new_rows = []
    for row in df.to_dict(orient="records"):
        key = (
            str(row.get("announcement_title", "")).strip(),
            str(row.get("fund_code", "")).strip(),
            str(row.get("date", "")),
        )
        if key in db_keys:
            continue
        new_rows.append(row)
    return new_rows


def insert_rows(rows: List[dict]) -> int:
    """批量插入新记录."""
    if not rows:
        logger.info("没有新的 files_info 记录需要插入。")
        return 0

    insert_sql = """
        INSERT INTO files_info (
            announcement_title,
            fund_code,
            date,
            doc_type_1,
            doc_type_2,
            announcement_link
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = [
        (
            str(row.get("announcement_title", "")).strip(),
            str(row.get("fund_code", "")).strip(),
            str(row.get("date", "")),
            row.get("doc_type_1"),
            row.get("doc_type_2"),
            row.get("announcement_link"),
        )
        for row in rows
    ]

    db_conf = get_db_config()
    conn = pymysql.connect(**db_conf)
    try:
        with conn.cursor() as cursor:
            cursor.executemany(insert_sql, values)
        conn.commit()
        logger.info("成功插入 %s 条新增记录到 files_info", len(values))
        return len(values)
    except Exception as exc:
        logger.exception("插入 files_info 新记录失败: %s", exc)
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    logger.info("开始执行 files_info 增量导入，Excel 路径: %s", EXCEL_PATH)

    if not os.path.exists(EXCEL_PATH):
        logger.error("Excel 文件不存在: %s", EXCEL_PATH)
        return

    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='list')
    except Exception as exc:
        logger.exception("读取 Excel 文件失败: %s", exc)
        return

    try:
        normalized_df = normalize_excel(df)
    except Exception as exc:
        logger.exception("标准化 Excel 数据失败: %s", exc)
        return

    logger.info("Excel 中有效记录数: %s", len(normalized_df))

    try:
        db_keys = fetch_db_keys()
    except Exception:
        return

    logger.info("数据库中已有 records 数: %s", len(db_keys))

    new_rows = get_new_rows(normalized_df, db_keys)
    logger.info("新的待插入记录数: %s", len(new_rows))

    if not new_rows:
        logger.info("没有新增记录，导入结束。")
        return

    try:
        insert_rows(new_rows)
    except Exception:
        logger.error("导入流程结束，存在失败记录。")
        return

    logger.info("files_info 增量导入流程完成。")


if __name__ == "__main__":
    main()


logging.shutdown()