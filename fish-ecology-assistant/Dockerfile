FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir pyyaml && pip install --no-cache-dir fastapi uvicorn

# 复制源码
COPY fish_ecology_assistant/ fish_ecology_assistant/
COPY config/ config/
COPY standalone.py .

# 迁移知识库
RUN python standalone.py migrate

# 暴露 API 端口
EXPOSE 8000

CMD ["python", "standalone.py", "serve"]
