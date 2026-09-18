# db_config.py

def get_db_config():
    """
    返回 MySQL 数据库全量数据连接的配置信息。
    """
    db_base_config = {
        'host': '127.0.0.1',          # 数据库主机 (WSL本地)
        'port': 3306,                 # 数据库端口
        'user': 'root',               # 数据库用户名 (compose 中未修改，默认为 root)
        'password': 'root_password',  # 【修改】对应 MYSQL_ROOT_PASSWORD
        'database': 'reits_db',       # 【修改】对应 MYSQL_DATABASE
        'charset': 'utf8mb4',         # 字符集
        'init_command': "SET SESSION collation_connection = 'utf8mb4_unicode_ci'" # 设置连接排序
    }
    return db_base_config

def get_db_announcement_config():
    """
    返回 MySQL 数据库announcement连接的配置信息。
    """
    db_announcement_config = {
        'host': '127.0.0.1',          # 数据库主机 (WSL本地)
        'port': 3306,                 # 数据库端口
        'user': 'root',               # 数据库用户名 (compose 中未修改，默认为 root)
        'password': 'root_password',  # 【修改】对应 MYSQL_ROOT_PASSWORD
        'database': 'reits_db',       # 【修改】对应 MYSQL_DATABASE
        'charset': 'utf8mb4',         # 字符集
        'init_command': "SET SESSION collation_connection = 'utf8mb4_unicode_ci'" # 设置连接排序
    }
    return db_announcement_config

def get_vector_db_config():
    """
    返回向量数据库（Milvus）的连接配置信息。
    """
    vector_db_config = {
        'host': 'localhost',  # 本地 Docker 部署的 Milvus
        'port': 19530,
        'user': 'root',
        'password': 'YOUR_MILVUS_PASSWORD'
    }
    return vector_db_config

def get_elasticsearch_config():
    """
    返回 Elasticsearch 数据库的连接配置信息。
    """
    elasticsearch_config = {
        'host': '127.0.0.1',          # Elasticsearch 服务主机
        'port': 9200,                 # Elasticsearch 服务端口
        'username': 'elastic',        # Elasticsearch 用户名
        'password': 'YOUR_ELASTICSEARCH_PASSWORD',    # Elasticsearch 密码
        'scheme': 'http'              # 明确指定连接协议为 http
    }
    return elasticsearch_config




