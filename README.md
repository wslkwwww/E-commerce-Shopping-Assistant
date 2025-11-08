# 智能电商导购助手 (E-commerce Shopping Assistant)

本项目是一个基于大型语言模型（LLM）和 LangChain 框架构建的智能电商信息查询 Agent 系统。系统集成了 **RAG (Retrieval-Augmented Generation)** 技术，通过 **FAISS** 向量数据库和 **BGE-M3** 嵌入模型实现高质量的商品语义搜索。后端使用 **MySQL** 数据库和 **Flask** API 服务，使其成为一个健壮、智能且适合商用场景的解决方案。

该系统能够深度理解用户的自然语言提问，并智能地执行语义搜索、查询商品信息和订单详情。

## 主要功能

- **智能语义搜索**: 用户可以使用模糊的、口语化的描述进行商品搜索（例如“适合夏天穿的凉快上衣”），系统能够理解其真实意图并返回最相关的商品。
- **订单查询**: 用户可以通过订单号查询订单的状态、金额、物流等详细信息。
- **复合问题理解**: 系统能够处理将商品和订单信息结合起来的复杂问题（例如：“订单12345里的那个耳机现在什么活动？”）。

## 技术架构

- **后端框架**: Flask
- **数据库**: MySQL
- **核心Agent框架**: LangChain
- **RAG 引擎**:
  - **向量数据库**: FAISS (Facebook AI Similarity Search)
  - **嵌入模型**: BGE (BAAI General Embedding)
- **大语言模型 (LLM)**: 可通过 `.env` 文件配置，兼容所有遵循 OpenAI API 格式的模型服务（如 LM Studio, Zeabur 等）。
- **Python 库**: `mysql-connector-python`, `langchain`, `faiss-cpu`, `sentence-transformers` 等。

## 文件结构

```
.
├── ecommerce_agent/
│   ├── agents/
│   │   ├── access_agent.py   # 接入Agent，负责理解和分发任务
│   │   ├── order_agent.py    # 订单查询工具
│   │   └── product_agent.py  # 商品RAG搜索工具
│   ├── app.py                # Flask 应用主文件
│   ├── config.py             # 项目配置文件
│   ├── mysql_db.py           # MySQL 数据库操作模块
│   └── qian.html             # 一个简单的前端交互页面
├── faiss_index/              # 自动生成的向量索引目录
├── download_models.py        # 自动化模型下载和向量索引创建脚本
├── import_csv.py             # 用于批量导入商品数据的脚本
├── new_products.csv          # 示例商品数据文件
├── requirements.txt          # 项目依赖
└── README.md                 # 本说明文件
```

---

## 快速开始

### 1. 环境准备

- **安装 MySQL**: 请确保您已安装并运行了 MySQL 数据库服务。
- **创建数据库**: 创建一个新的数据库（例如 `ecommerce_db`）供本项目使用。
- **安装 Python 依赖**: 在项目根目录下打开终端，运行以下命令安装所有必需的库：
  ```bash
  pip install -r requirements.txt
  ```

### 2. 配置项目

- **创建配置文件**: 将 `.env.example` 文件复制一份并重命名为 `.env`。
- **编辑配置文件**: 打开刚刚创建的 `.env` 文件，根据您的环境完成以下配置：

  - **大语言模型 (LLM) 配置**:
    - `BASE_URL`: 您的 LLM 服务地址。
    - `OPENAI_API_KEY`: 您的 API 密钥。

  - **MySQL 数据库配置**:
    - `MYSQL_HOST`: 数据库主机地址（通常是 `localhost`）。
    - `MYSQL_PORT`: 数据库端口号（默认为 `3306`）。
    - `MYSQL_USER`: 数据库用户名。
    - `MYSQL_PASSWORD`: 您的数据库密码。
    - `MYSQL_DB`: 您为项目创建的数据库名称。

### 3. 导入商品数据

本项目提供了一个脚本，用于将 CSV 文件中的商品数据批量导入数据库。

- **准备数据**: 您可以使用我们提供的 `new_products.csv` 作为模板。
- **执行导入**: 在终端中运行以下命令：
  ```bash
  python import_csv.py new_products.csv
  ```
  该命令会将 `new_products.csv` 中的所有商品数据导入到您的 MySQL 数据库中。

### 4. 下载模型并创建向量索引

这是**最关键**的一步。运行我们提供的自动化脚本，它将完成所有模型下载和数据处理工作。

在项目根目录下运行：
```bash
python download_models.py
```
该脚本会自动：
1.  下载 `bge-large-zh-v1.5` 嵌入模型。
2.  从您的 MySQL 数据库中读取所有商品信息。
3.  将商品信息向量化，并创建一个 FAISS 索引，保存在 `faiss_index` 目录中。

### 5. 启动后端服务

一切准备就绪后，运行以下命令来启动后端 Flask 应用：

```bash
python -m ecommerce_agent.app
```

当您看到终端输出 `Running on http://0.0.0.0:5000` 时，表示后端服务已成功启动。

### 6. 进行查询

您可以通过多种方式与智能助手交互：

- **使用 `curl` (推荐)**: 打开一个新的终端，使用 `curl` 命令模拟 API 请求。
  - **语义搜索**:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d "{\"question\": \"有没有适合夏天穿的凉快上衣？\"}" http://localhost:5000/api/query
    ```
  - **查询订单**:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d "{\"question\": \"查一下订单12345\"}" http://localhost:5000/api/query
    ```

- **使用前端页面**: 在浏览器中直接打开 `ecommerce_agent/qian.html` 文件，在输入框中输入您的问题并提交。

---
