import logging
from ecommerce_agent.mysql_db import get_db_connection


class OrderAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 初始化订单查询工具
        self.order_tool = self._create_order_tool()

    def _create_order_tool(self):
        """创建订单查询工具"""
        from langchain_core.tools import StructuredTool

        def query_order_with_product(order_id: str):
            """查询订单信息（含商品ID）"""
            self.logger.info(f"OrderAgent 工具被调用: query_order_with_product, 参数 order_id='{order_id}'")
            conn = get_db_connection()
            if not conn:
                self.logger.error("OrderAgent 无法获取数据库连接。")
                return "错误：无法连接到数据库。"

            try:
                cursor = conn.cursor(dictionary=True)  # 使用字典游标，方便按列名获取数据
                cursor.execute("""
                               SELECT status, logistics_info, total_amount, create_time, product_ids, receive_time
                               FROM orders
                               WHERE order_id = %s
                               """, (order_id,))
                result = cursor.fetchone()
                conn.close()

                if not result:
                    self.logger.warning(f"在数据库中未找到订单: '{order_id}'")
                    return f"未找到订单编号为 {order_id} 的信息"
                
                self.logger.info(f"数据库查询成功，订单 '{order_id}' 的信息: {result}")
                # 从字典中安全地获取值
                status = result.get("status")
                logistics = result.get("logistics_info")
                amount = result.get("total_amount")
                create_time = result.get("create_time")
                product_ids = result.get("product_ids")
                receive_time = result.get("receive_time")

                response = f"订单 {order_id} 信息：\n"
                response += f"- 状态：[{status or '未知'}]\n"
                response += f"- 总金额：[{amount or '未知'}元]\n"
                response += f"- 创建时间：[{create_time or '未知'}]\n"
                response += f"- 签收时间：[{receive_time or '未知'}]\n"
                response += f"- 商品ID：[{product_ids or '未知'}]\n"
                if logistics:
                    response += f"- 物流信息：[{logistics}]"
                
                self.logger.info(f"为订单 '{order_id}' 生成的最终回复: {response}")
                return response
            except Exception as e:
                self.logger.error(f"查询订单 '{order_id}' 时发生数据库错误: {e}", exc_info=True)
                return f"查询失败：{str(e)}"

        return StructuredTool.from_function(
            func=query_order_with_product,
            name="query_order",
            description="查询订单详情（含商品ID），参数为order_id（订单编号，如12345）"
        )

    def get_tool(self):
        """提供给接入Agent的工具接口"""
        return self.order_tool