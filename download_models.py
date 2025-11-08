import subprocess
import sys
import os

# --- 新增：向量化配置 ---
from ecommerce_agent import mysql_db
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 定义模型和索引路径
# 模型将从ModelScope下载到 'embedding' 目录
EMBEDDING_DOWNLOAD_DIR = "embedding"
# BGE模型在下载后的路径将在 create_vector_store 中动态查找
FAISS_INDEX_PATH = "faiss_index"

# --- 模型配置 ---
# 将所有需要下载的模型ID放在这个列表里
# 未来可以轻松添加新的模型，例如LLM
MODELS_TO_DOWNLOAD = [
    "Ceceliachenen/bge-large-zh-v1.5", # 用于生成高质量文本向量
    # 示例：未来若要下载Qwen2的1.5B模型，只需取消下面的注释
    # "qwen/Qwen2-1.5B-Instruct-GGUF",
]

def run_command(command):
    """
    执行一个shell命令并实时打印其输出。
    """
    print(f"\n--- 运行命令: {' '.join(command)} ---")
    try:
        # 使用 Popen 以便实时捕获输出
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # 实时读取并打印输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # 获取最终的返回码
        rc = process.poll()
        if rc != 0:
            print(f"--- 命令执行失败，退出码: {rc} ---")
            return False
        print(f"--- 命令执行成功 ---")
        return True
    except FileNotFoundError:
        print(f"错误: 命令 '{command}' 未找到。")
        print("请确保相关程序已安装并在系统的 PATH 环境变量中。")
        return False
    except Exception as e:
        print(f"发生未知错误: {e}")
        return False

def setup_models():
    """
    主函数，负责安装依赖并下载所有模型。
    """
    # 定义下载目录
    download_dir = EMBEDDING_DOWNLOAD_DIR
    # 获取绝对路径
    download_path = os.path.abspath(download_dir)

    print(">>> 步骤 1/4: 检查并安装核心依赖库...")
    # 使用 sys.executable 确保我们用的是当前环境的 pip
    pip_command = [
        sys.executable, "-m", "pip", "install",
        "modelscope", "faiss-cpu", "sentence-transformers"
    ]
    if not run_command(pip_command):
         print("!!! 安装核心依赖失败。脚本中止。")
         return

    print(f"\n>>> 步骤 2/4: 确保下载目录存在...")
    os.makedirs(download_path, exist_ok=True)
    print(f"模型将被下载到: {download_path}")

    print("\n>>> 步骤 3/4: 开始下载模型...")
    all_downloads_successful = True
    for model_id in MODELS_TO_DOWNLOAD:
        print(f"\n--- 准备下载: {model_id} ---")
        # 在命令中加入 --cache_dir 参数
        if not run_command(["modelscope", "download", "--model", model_id, "--cache_dir", download_path]):
            print(f"!!! 下载模型 {model_id} 失败。")
            all_downloads_successful = False
    
    print("\n" + "="*50)
    if all_downloads_successful:
        print("所有模型均已成功下载或已存在于缓存中。")
    else:
        print("部分模型下载失败，请检查上面的日志获取详细信息。")
    print("="*50)


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

def create_vector_store():
    """
    从数据库读取商品信息，生成向量索引并保存到本地。
    """
    print("\n>>> 步骤 4/4: 创建商品向量索引...")

    # 1. 动态查找并检查嵌入模型是否存在
    embedding_model_path = find_model_path(EMBEDDING_DOWNLOAD_DIR, "Ceceliachenen", "bge-large-zh-v1.5")
    if not embedding_model_path or not os.path.exists(embedding_model_path):
        print(f"!!! 错误: 无法在 '{os.path.join(EMBEDDING_DOWNLOAD_DIR, 'Ceceliachenen')}' 目录下找到 bge-large-zh-v1.5 模型。")
        print("请确保模型已通过脚本成功下载。")
        return False
    print(f"--- 找到嵌入模型路径: {embedding_model_path}")

    # 2. 加载嵌入模型
    print("--- 正在加载嵌入模型 (这可能需要一些时间)...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_path)
    except Exception as e:
        print(f"!!! 加载嵌入模型失败: {e}")
        return False
    print("--- 嵌入模型加载成功。")

    # 3. 从数据库获取商品数据
    print("--- 正在从数据库获取商品数据...")
    products = mysql_db.get_all_products_for_vectorization()
    if not products:
        print("--- 数据库中没有找到商品，或无法连接数据库。跳过向量化。")
        return True # Not a fatal error, maybe the db is just empty.

    # 4. 准备 LangChain 文档
    print(f"--- 准备将 {len(products)} 件商品进行向量化...")
    documents = []
    for product in products:
        content = f"商品名称: {product['name']}\n商品描述: {product['description']}"
        # 将商品ID存储在元数据中，以便后续检索
        metadata = {"product_id": product['id']}
        documents.append(Document(page_content=content, metadata=metadata))

    # 5. 创建并保存 FAISS 索引
    try:
        print("--- 正在创建 FAISS 索引 (这可能需要几分钟)...")
        vector_store = FAISS.from_documents(documents, embeddings)
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        vector_store.save_local(FAISS_INDEX_PATH)
        print(f"向量索引成功创建并保存至 '{FAISS_INDEX_PATH}' 目录。")
        return True
    except Exception as e:
        print(f"!!! 创建或保存 FAISS 索引时发生错误: {e}")
        return False


if __name__ == "__main__":
    # 在 Docker 构建阶段，我们只下载模型。
    # 向量索引将在应用启动时根据数据库动态创建。
    setup_models()