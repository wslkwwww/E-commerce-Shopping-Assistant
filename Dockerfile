# 使用官方的 Python 3.10 slim 版本作为基础镜像
FROM python:3.10-slim

# 安装一些基础的系统依赖，git-lfs 用于从 Hugging Face 下载大文件
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 初始化 git-lfs
RUN git lfs install

# 设置工作目录
WORKDIR /app

# 为了利用 Docker 的层缓存机制，先复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖，使用 --no-cache-dir 减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目的所有文件到工作目录
COPY . .

# 运行模型下载和向量索引创建脚本
# 这一步会下载所有必要的模型并生成 FAISS 索引
RUN python download_models.py

# 暴露 Flask 应用的端口
EXPOSE 5000

# 设置环境变量，确保 Python 输出能直接打印到终端
ENV PYTHONUNBUFFERED=1

# 启动应用的命令
# 注意：我们使用 0.0.0.0 作为主机，以允许从容器外部访问
CMD ["python", "-m", "ecommerce_agent.app"]