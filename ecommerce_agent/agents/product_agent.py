import logging
import os
from langchain_core.tools import StructuredTool
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from ecommerce_agent.mysql_db import get_db_connection

# --- RAG 配置 ---
EMBEDDING_DOWNLOAD_DIR = "embedding"
FAISS_INDEX_PATH = "faiss_index"

def find_model_path(base_dir, owner, model_id_prefix):
    """
    动态查找模型路径，以兼容 Windows 下符号链接创建失败的情况。
    它会自动处理 modelscope 将 '.' 替换为 '___' 的命名规则。
    """
    owner_path = os.path.join(base_dir, owner)
    if not os.path.exists(owner_path):
        return None
    
    # 处理 ModelScope 的命名转换规则
    expected_folder_prefix = model_id_prefix.replace('.', '___')
    
    for item in os.listdir(owner_path):
        if item.startswith(expected_folder_prefix):
            return os.path.join(owner_path, item)
    return None

class ProductAgent:
    def __init__(self, **kwargs):
        """
        初始化商品Agent。
        这个Agent现在使用RAG（FAISS向量库 + MySQL）进行商品搜索。
        """
        self.logger = logging.getLogger(__name__)
        self.vector_store = self._init_vector_store()
        
        # 初始化工具
        self.search_tool = self._create_search_tool()
        self.product_tool = self._create_product_tool()

    def _init_vector_store(self):
        """加载嵌入模型和FAISS索引，初始化向量数据库。"""
        self.logger.info("正在初始化 ProductAgent 的 RAG 组件...")
        
        # 1. 动态查找并加载嵌入模型
        embedding_model_path = find_model_path(EMBEDDING_DOWNLOAD_DIR, "Ceceliachenen", "bge-large-zh-v1.5")
        if not embedding_model_path or not os.path.exists(embedding_model_path):
            self.logger.error(f"错误: 无法在 '{os.path.join(EMBEDDING_DOWNLOAD_DIR, 'Ceceliachenen')}' 目录下找到 bge-large-zh-v1.5 模型。")
            return None
        
        self.logger.info(f"找到嵌入模型路径: {embedding_model_path}")
        try:
            embeddings = HuggingFaceEmbeddings(model_name=embedding_model_path)
        except Exception as e:
            self.logger.error(f"加载嵌入模型失败: {e}", exc_info=True)
            return None
        self.logger.info("嵌入模型加载成功。")

        # 2. 检查并加载FAISS索引
        if not os.path.exists(FAISS_INDEX_PATH):
            self.logger.error(f"错误: FAISS 索引目录 '{FAISS_INDEX_PATH}' 不存在。")
            self.logger.error("请先运行 'python download_models.py' 来创建索引。")
            return None
            
        try:
            vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            self.logger.info("FAISS 索引加载成功。")
            return vector_store
        except Exception as e:
            self.logger.error(f"加载 FAISS 索引失败: {e}", exc_info=True)
            return None

    def _create_search_tool(self):
        """创建基于RAG的商品语义搜索工具"""

        def search_products_by_semantic_query(query: str):
            """通过自然语言描述进行语义搜索，查找相关商品。"""
            self.logger.info(f"ProductAgent RAG工具被调用, 查询: '{query}'")
            
            if not self.vector_store:
                return "错误: 向量数据库未成功初始化，无法执行语义搜索。"

            # 1. 使用FAISS进行语义检索，获取包含商品ID和分数的文档
            try:
                # 使用 similarity_search_with_score 来获取分数
                docs_and_scores = self.vector_store.similarity_search_with_score(query, k=5)
                if not docs_and_scores:
                    self.logger.warning(f"向量数据库中未找到与 '{query}' 相关的商品。")
                    return f"未找到与 '{query}' 相关的商品。"
            except Exception as e:
                self.logger.error(f"执行向量检索时出错: {e}", exc_info=True)
                return f"语义搜索失败: {str(e)}"

            # 2. 记录详细的检索结果（包含分数）
            self.logger.info("向量数据库检索结果 (分数越低越相关):")
            product_ids = []
            for doc, score in docs_and_scores:
                product_id = doc.metadata.get("product_id")
                self.logger.info(f"  - Product ID: {product_id}, Score: {score:.4f}")
                if product_id:
                    product_ids.append(product_id)

            if not product_ids:
                return "找到了相似的描述，但无法关联到具体的商品ID。"
            
            self.logger.info(f"语义搜索找到商品ID: {product_ids}")

            # 3. 使用商品ID从MySQL获取最新、最全的商品信息
            conn = get_db_connection()
            if not conn:
                return "错误：成功进行了语义搜索，但无法连接到数据库以获取商品详情。"
            
            try:
                cursor = conn.cursor(dictionary=True)
                # 使用 IN 子句一次性获取所有商品信息，并用 FIELD 函数保持向量搜索的顺序
                format_strings = ','.join(['%s'] * len(product_ids))
                sql_query = f"""
                    SELECT id, name, specifications, price, activity
                    FROM products
                    WHERE id IN ({format_strings})
                    ORDER BY FIELD(id, {format_strings})
                """
                cursor.execute(sql_query, product_ids * 2) # product_ids 需要重复两次
                results = cursor.fetchall()
                conn.close()

                if not results:
                    return "数据库中未找到向量索引返回的商品ID，数据可能不同步。"

                # 4. 格式化最终结果
                response = f"根据您的描述 '{query}'，为您找到以下最相关的商品：\n"
                for i, product_info in enumerate(results, 1):
                    response += f"{i}. 商品ID: {product_info.get('id', '未知')}\n"
                    response += f"   名称: {product_info.get('name', '未知')}\n"
                    response += f"   规格: {product_info.get('specifications', '未知')}\n"
                    response += f"   价格: {product_info.get('price', '未知')}\n"
                    response += f"   活动: {product_info.get('activity', '无')}\n\n"
                
                self.logger.info(f"为查询 '{query}' 生成的最终RAG回复: {response.strip()}")
                return response.strip()
            except Exception as e:
                self.logger.error(f"从MySQL获取商品详情时出错: {e}", exc_info=True)
                if conn and conn.is_connected():
                    conn.close()
                return f"数据库查询失败: {str(e)}"

        return StructuredTool.from_function(
            func=search_products_by_semantic_query,
            name="search_products",
            description="通过自然语言描述进行语义搜索，查找相关商品。例如：'适合户外徒步的鞋'、'送给女朋友的生日礼物'"
        )

    def _create_product_tool(self):
        """创建商品查询工具（基于MySQL数据库）"""

        def query_product_info(product_id: str):
            """通过商品ID查询商品详情"""
            self.logger.info(f"ProductAgent 工具被调用: query_product_info, 参数 product_id='{product_id}'")
            conn = get_db_connection()
            if not conn:
                self.logger.error("ProductAgent 无法获取数据库连接。")
                return "错误：无法连接到数据库。"
            
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                p = cursor.fetchone()
                conn.close()

                if p:
                    response = (f"商品ID {product_id} 的详细信息：\n"
                                f"- 名称：{p.get('name', '未知')}\n"
                                f"- 规格：{p.get('specifications', '未知')}\n"
                                f"- 描述：{p.get('description', '未知')}\n"
                                f"- 价格：{p.get('price', '未知')}\n"
                                f"- 活动：{p.get('activity', '未知')}")
                    self.logger.info(f"为商品ID '{product_id}' 查询成功。")
                    return response
                
                self.logger.warning(f"在数据库中未找到商品ID: '{product_id}'")
                return f"数据库中未找到商品ID为 {product_id} 的信息"
            except Exception as e:
                self.logger.error(f"查询商品ID '{product_id}' 时发生数据库错误: {e}", exc_info=True)
                if conn.is_connected():
                    conn.close()
                return f"数据库查询失败：{str(e)}"

        return StructuredTool.from_function(
            func=query_product_info,
            name="query_product",
            description="查询商品详情（含规格），参数为product_id（商品ID，例如'001'）"
        )

    def get_tools(self):
        """提供给接入Agent的工具接口"""
        return [self.search_tool, self.product_tool]