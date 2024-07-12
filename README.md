# Py-queue-db

Py-queue-db 是一个开源项目，旨在提供一个类似 Kafka 的消息队列数据库的 Python 实现。该项目使用 SQLite 作为后端存储，并提供了一个简单的 HTTP API 来发布、轮询和提交消息。

## 功能特性

- **消息发布**：通过 HTTP POST 请求发布消息到指定主题。
- **消息轮询**：通过 HTTP GET 请求从指定主题轮询消息。
- **消息提交**：通过 HTTP POST 请求提交消费者组的偏移量。

## 安装

1. 克隆项目仓库：
    ```bash
    git clone https://github.com/zhangheli/py-queue-db.git
    cd py-queue-db
    ```

2. 安装依赖：
    ```bash
    pip install aiohttp
    ```

## 使用方法

1. 启动服务器：
    ```bash
    python py-queue-db.py
    ```

2. 发布消息：
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"topic": "test_topic", "message": {"key": "value"}}' http://localhost:8080/publish
    ```

3. 轮询消息：
    ```bash
    curl "http://localhost:8080/poll?topic=test_topic&consumer_group=test_group&timeout=5"
    ```

4. 提交偏移量：
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"topic": "test_topic", "consumer_group": "test_group", "offset": 10}' http://localhost:8080/commit
    ```

## API 文档

### 发布消息

- **URL**: `/publish`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "topic": "string",
        "message": "object"
    }
    ```
- **Response**:
    ```json
    {
        "status": "ok",
        "message_id": "integer"
    }
    ```

### 轮询消息

- **URL**: `/poll`
- **Method**: `GET`
- **Query Parameters**:
    - `topic`: 主题名称
    - `consumer_group`: 消费者组名称
    - `timeout`: 超时时间（秒），默认值为 0
- **Response**:
    ```json
    {
        "messages": [
            {
                "id": "integer",
                "message": "object"
            }
        ]
    }
    ```

### 提交偏移量

- **URL**: `/commit`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "topic": "string",
        "consumer_group": "string",
        "offset": "integer"
    }
    ```
- **Response**:
    ```json
    {
        "status": "ok"
    }
    ```

## 贡献

欢迎贡献代码、报告问题或提出建议。请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解更多信息。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。
