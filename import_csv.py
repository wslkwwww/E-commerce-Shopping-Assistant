import argparse
import os
from ecommerce_agent import mysql_db

def main():
    """
    主函数，用于解析命令行参数并执行CSV导入。
    """
    parser = argparse.ArgumentParser(
        description="将商品数据从CSV文件批量导入到MySQL数据库。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "csv_file",
        help="要导入的CSV文件的路径。"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="在导入前，先运行数据库初始化（创建表）。"
    )
    
    print("\n--- CSV商品数据导入工具 ---")
    print("""
    请确保您的CSV文件包含以下列标题:
    id,name,description,specifications,price,activity
    
    示例:
    id,name,description,specifications,price,activity
    P001,新款智能手表,健康监测,黑色/白色,1299元,新品8折
    P002,蓝牙降噪耳机,长续航,白色,799元,满500减50
    """)

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.csv_file):
        print(f"错误：找不到文件 '{args.csv_file}'。请检查路径是否正确。")
        return

    # （可选）初始化数据库
    if args.init:
        print("\n正在执行数据库初始化...")
        mysql_db.init_database()
        print("数据库初始化完成。")

    # 执行批量导入
    print(f"\n正在从 '{args.csv_file}' 文件导入数据...")
    mysql_db.batch_insert_products_from_csv(args.csv_file)
    print("---------------------------------")

if __name__ == "__main__":
    main()