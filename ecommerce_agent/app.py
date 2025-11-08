import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from .config import (
    OPENAI_API_KEY, BASE_URL, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
)
from .agents import AccessAgent
from . import mysql_db # 导入新的MySQL模块

# --- 日志配置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 在启动时初始化数据库
with app.app_context():
    logger.info("Flask 应用启动，正在检查并初始化数据库...")
    mysql_db.init_database()
    # 可选：如果数据库为空，可以插入测试数据
    # mysql_db.insert_test_data()
    logger.info("数据库初始化完成。")

# 初始化接入Agent
llm_config = {
    "api_key": OPENAI_API_KEY,
    "base_url": BASE_URL,
    "model_name": "gemini-2.5-pro",
    "temperature": 0.0,
    "max_tokens": 4096
}

access_agent = AccessAgent(
    llm_config=llm_config
)


# API接口
@app.route('/api/query', methods=['POST'])
def query():
    """处理用户查询的API接口"""
    data = request.json
    if not data or "question" not in data:
        logger.warning("API 调用缺少 'question' 参数")
        return jsonify({"error": "缺少参数: question"}), 400

    try:
        question = data["question"]
        logger.info(f"接收到问题: '{question}'")
        response = access_agent.handle_question(question)
        logger.info(f"返回给用户的最终答案: '{response}'")
        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        logger.error(f"处理请求时发生严重错误: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )
