FROM python:3.12-slim

# 时区（可选）
ENV TZ=Asia/Shanghai

WORKDIR /app

# 先装依赖，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷代码
COPY app.py .
COPY templates ./templates

# 把模型放进去（见下方说明）

RUN apt-get update && apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /root/.u2net && \
    wget -O /root/.u2net/u2net.onnx \
    https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

EXPOSE 5000

CMD ["python", "app.py"]
