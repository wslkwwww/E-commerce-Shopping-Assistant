import os
from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
# __file__ 是当前文件路径, os.path.dirname() 获取其目录
# os.path.join(..., '..') 回到上级目录，即项目根目录
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("警告: 未找到 .env 文件。请确保您已根据 .env.example 创建了 .env 文件。")

# --- 从环境变量加载配置 ---

# LLM 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# MySQL 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306)) # 端口号应为整数
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# Flask 配置
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000)) # 端口号应为整数
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ('true', '1', 't')

# --- 移除的旧配置 ---
# EMBEDDING_MODEL_PATH 和 PRODUCT_VECTOR_PATH 已不再需要
# DB_TYPE 和 SQLITE_DB_PATH 也已废弃
