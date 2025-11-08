import mysql.connector
from mysql.connector import Error
import csv
import logging
from ecommerce_agent import config

logger = logging.getLogger(__name__)

# --- 数据库连接 ---

def get_db_connection():
    """建立到MySQL数据库的连接。"""
    logger.info(f"正在尝试连接到MySQL数据库: host={config.MYSQL_HOST}, db={config.MYSQL_DB}")
    try:
        connection = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB
        )
        if connection.is_connected():
            logger.info("数据库连接成功。")
            return connection
    except Error as e:
        logger.error(f"连接MySQL时出错: {e}", exc_info=True)
        # 提醒用户检查密码
        if "Access denied" in str(e):
            logger.warning("数据库访问被拒绝。提醒: 请检查 .env 文件中的数据库凭据是否正确。")
        return None

# --- 表初始化 ---

def init_database():
    """
    初始化数据库，如果表不存在，则创建 'products' 和 'orders' 表。
    """
    conn = get_db_connection()
    if not conn:
        print("无法连接到数据库。正在中止初始化。")
        return

    cursor = conn.cursor()
    try:
        # 创建 products 表
        print("正在创建 'products' 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                specifications VARCHAR(255),
                price VARCHAR(255),
                activity TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("表 'products' 已创建或已存在。")

        # 创建 orders 表
        print("正在创建 'orders' 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255),
                product_ids TEXT,
                status VARCHAR(255),
                total_amount DECIMAL(10, 2),
                create_time DATETIME,
                pay_time DATETIME,
                ship_time DATETIME,
                receive_time DATETIME,
                logistics_info TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("表 'orders' 已创建或已存在。")

    except Error as e:
        print(f"创建表时出错: {e}")
    finally:
        cursor.close()
        conn.close()

# --- 数据导入 ---

def insert_test_data():
    """将初始测试数据插入数据库，用于产品和订单。"""
    conn = get_db_connection()
    if not conn:
        print("无法连接到数据库。正在中止测试数据插入。")
        return
    
    cursor = conn.cursor()
    try:
        # 15条测试商品数据
        products = [
            ("001", "纯棉T恤", "100%纯棉材质，透气舒适，适合夏季穿着", "S/M/L/XL", "99元", "满200减30，可叠加使用"),
            ("002", "牛仔裤", "修身版型，弹力面料，经典款式", "28/29/30/31/32（腰围）", "159元", "第二件半价"),
            ("003", "运动鞋", "轻便透气，缓震鞋底，适合跑步健身", "39/40/41/42/43/44", "299元", "会员专享8折"),
            ("004", "连衣裙", "雪纺材质，碎花图案，优雅大方", "S/M/L", "179元", "满300减50"),
            ("005", "夹克外套", "防风防水面料，春秋季适用", "M/L/XL/XXL", "259元", "新品上市，暂无活动"),
            ("006", "羊毛衫", "含羊毛成分，保暖舒适", "S/M/L/XL", "199元", "满2件减100"),
            ("007", "休闲裤", "棉质混纺，宽松版型，日常穿着舒适", "M/L/XL", "129元", "满150减20"),
            ("008", "卫衣", "加绒加厚，连帽设计，时尚休闲", "S/M/L/XL", "149元", "限时折扣，直降30元"),
            ("009", "衬衫", "免烫处理，商务休闲两用", "38/39/40/41/42", "169元", "满300减60"),
            ("010", "羽绒服", "90%白鸭绒填充，轻便保暖", "M/L/XL/XXL", "499元", "预售优惠，定金50抵100"),
            ("011", "帆布鞋", "经典款式，舒适百搭，适合日常穿着", "35/36/37/38/39/40", "79元", "买一送一"),
            ("012", "背包", "大容量设计，防水面料，适合通勤旅行", "均码（黑色/灰色/蓝色）", "199元", "满200减40"),
            ("013", "帽子", "棉质材质，防晒透气，时尚简约", "均码（可调节）", "59元", "3件起9折"),
            ("014", "围巾", "羊毛混纺，柔软保暖，多种颜色可选", "均码（红色/蓝色/灰色/黑色）", "89元", "满100减20"),
            ("015", "手套", "加绒加厚，触屏设计，冬季必备", "M/L（黑色/棕色）", "69元", "买二送一")
        ]
        
        product_query = "INSERT IGNORE INTO products (id, name, description, specifications, price, activity) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.executemany(product_query, products)
        print(f"插入了 {cursor.rowcount} 条测试商品数据。")

        # 10条测试订单数据
        test_orders = [
            ("12345", "user001", "001,003", "已签收", 398.0, "2023-10-01 09:30:00", "2023-10-01 10:15:00", "2023-10-02 14:20:00", "2023-10-04 16:45:00", "圆通快递: YT1234567890"),
            ("12346", "user002", "002", "已发货", 159.0, "2023-10-02 11:20:00", "2023-10-02 11:30:00", "2023-10-03 08:10:00", None, "中通快递: ZT0987654321"),
            ("12347", "user003", "004,006", "已付款", 378.0, "2023-10-02 15:40:00", "2023-10-02 16:05:00", None, None, None),
            ("12348", "user004", "005", "待付款", 259.0, "2023-10-03 09:10:00", None, None, None, None),
            ("12349", "user005", "007,008,009", "已签收", 447.0, "2023-10-03 14:30:00", "2023-10-03 15:00:00", "2023-10-04 09:20:00", "2023-10-06 11:30:00", "顺丰速运: SF1122334455"),
            ("12350", "user006", "010", "已取消", 499.0, "2023-10-04 10:20:00", None, None, None, None),
            ("12351", "user007", "001,008", "已发货", 248.0, "2023-10-04 16:50:00", "2023-10-04 17:10:00", "2023-10-05 10:30:00", None, "韵达快递: YD5566778899"),
            ("12352", "user008", "003,005", "已付款", 558.0, "2023-10-05 08:40:00", "2023-10-05 09:05:00", None, None, None),
            ("12353", "user009", "006,007", "已签收", 328.0, "2023-10-05 13:20:00", "2023-10-05 14:00:00", "2023-10-06 09:15:00", "2023-10-08 15:20:00", "圆通快递: YT9876543210"),
            ("12354", "user010", "002,009", "待付款", 328.0, "2023-10-06 11:10:00", None, None, None, None)
        ]
        
        order_query = "INSERT IGNORE INTO orders (order_id, user_id, product_ids, status, total_amount, create_time, pay_time, ship_time, receive_time, logistics_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(order_query, test_orders)
        print(f"插入了 {cursor.rowcount} 条测试订单数据。")
        
        conn.commit()

    except Error as e:
        print(f"插入测试数据时出错: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def batch_insert_products_from_csv(file_path):
    """
    从CSV文件读取商品数据并将其插入到 'products' 表中。
    CSV文件应包含与表列匹配的标题行:
    id,name,description,specifications,price,activity
    """
    conn = get_db_connection()
    if not conn:
        print("无法连接到数据库。正在中止CSV导入。")
        return
        
    cursor = conn.cursor()
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            products_to_insert = []
            for row in csv_reader:
                products_to_insert.append(tuple(row.get(col) for col in ['id', 'name', 'description', 'specifications', 'price', 'activity']))

            if products_to_insert:
                # 使用 ON DUPLICATE KEY UPDATE 来插入或更新数据
                query = """
                    INSERT INTO products (id, name, description, specifications, price, activity) 
                    VALUES (%s, %s, %s, %s, %s, %s) 
                    ON DUPLICATE KEY UPDATE 
                        name=VALUES(name), 
                        description=VALUES(description), 
                        specifications=VALUES(specifications), 
                        price=VALUES(price), 
                        activity=VALUES(activity)
                """
                cursor.executemany(query, products_to_insert)
                conn.commit()
                print(f"成功从 {file_path} 插入/更新了 {cursor.rowcount} 件商品。")

    except FileNotFoundError:
        print(f"错误: 未找到文件 {file_path}。")
    except Error as e:
        print(f"CSV导入期间数据库错误: {e}")
        conn.rollback()
    except Exception as e:
        print(f"发生意外错误: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("正在初始化MySQL数据库...")
    init_database()
    print("\n正在插入测试数据...")
    insert_test_data()
    print("\n数据库设置完成。")
    # CSV导入示例 (取消注释并提供正确路径以使用):
    # print("\n尝试从CSV导入...")
    # batch_insert_products_from_csv('path/to/your/products.csv')

def get_all_products_for_vectorization():
    """获取所有商品的核心信息用于向量化。"""
    conn = get_db_connection()
    if not conn:
        print("无法连接到数据库，无法获取商品列表。")
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, description FROM products")
        products = cursor.fetchall()
        return products
    except Error as e:
        print(f"获取所有商品时出错: {e}")
        return []
    finally:
        if conn.is_connected():
            conn.close()