# ARK API 使用指南

ARK API 是字节跳动推出的豆包大模型服务，提供高质量的 AI 对话能力。本指南将帮助你配置 claude-code-proxy 以使用 ARK API。

## 目录

- [快速开始](#快速开始)
- [获取 ARK API Key](#获取-ark-api-key)
- [配置代理](#配置代理)
- [测试连接](#测试连接)
- [与 Claude Code 集成](#与-claude-code-集成)
- [支持的功能](#支持的功能)
- [故障排查](#故障排查)
- [API 特性对比](#api-特性对比)

## 快速开始

### 1. 获取 ARK API Key

1. 访问 [豆包大模型服务控制台](https://console.volcengine.com/ark)
2. 创建应用并获取 API Key
3. 创建推理接入点并记录端点 ID（格式：`ep-xxxxxxxxxx-xxxxx`）

### 2. 配置环境变量

复制 ARK 配置示例：
```bash
cp .env.ark.example .env
```

编辑 `.env` 文件：
```bash
# ARK API Key (豆包大模型服务)
ARK_API_KEY="your-ark-api-key-here"

# ARK API Base URL
OPENAI_BASE_URL="https://ark-cn-beijing.bytedance.net/api/v3"

# ARK Model Configuration (替换为你的端点 ID)
BIG_MODEL="ep-xxxxxxxxxx-xxxxx"
MIDDLE_MODEL="ep-xxxxxxxxxx-xxxxx"
SMALL_MODEL="ep-xxxxxxxxxx-xxxxx"

# 可选：服务器设置
HOST="0.0.0.0"
PORT="8082"
LOG_LEVEL="INFO"
```

### 3. 启动代理服务器

```bash
# 安装依赖（如果还没有安装）
uv sync

# 启动代理服务器
uv run python -m src.main
```

服务器将在 `http://localhost:8082` 启动。

### 4. 测试连接

运行测试脚本验证配置：
```bash
python test_ark.py
```

## 获取 ARK API Key

### 步骤详解

1. **访问控制台**
   - 前往 [豆包大模型服务控制台](https://console.volcengine.com/ark)
   - 使用字节跳动账号登录

2. **创建应用**
   - 点击"创建应用"
   - 填写应用名称和描述
   - 选择适合的应用类型

3. **获取 API Key**
   - 在应用详情页面找到 API Key
   - 复制并保存 API Key

4. **创建推理接入点**
   - 选择合适的模型（如：豆包主力模型）
   - 配置推理参数
   - 获取端点 ID（格式：`ep-xxxxxxxxxx-xxxxx`）

## 配置代理

### 基本配置

最小化配置只需要三个环境变量：

```bash
ARK_API_KEY="your-ark-api-key"
OPENAI_BASE_URL="https://ark-cn-beijing.bytedance.net/api/v3"
BIG_MODEL="ep-xxxxxxxxxx-xxxxx"
```

### 高级配置

完整配置选项：

```bash
# === ARK API 配置 ===
ARK_API_KEY="your-ark-api-key"
OPENAI_BASE_URL="https://ark-cn-beijing.bytedance.net/api/v3"

# === 模型映射 ===
# Claude Code 会将不同的 Claude 模型映射到这些端点
BIG_MODEL="ep-xxxxxxxxxx-xxxxx"      # 用于 Claude Opus
MIDDLE_MODEL="ep-xxxxxxxxxx-xxxxx"   # 用于 Claude Sonnet
SMALL_MODEL="ep-xxxxxxxxxx-xxxxx"    # 用于 Claude Haiku

# === 客户端验证（可选）===
# 如果设置，客户端必须提供匹配的 API key
ANTHROPIC_API_KEY="your-expected-client-key"

# === 服务器设置 ===
HOST="0.0.0.0"
PORT="8082"
LOG_LEVEL="INFO"

# === 性能设置 ===
MAX_TOKENS_LIMIT="4096"
MIN_TOKENS_LIMIT="100"
REQUEST_TIMEOUT="90"
MAX_RETRIES="2"
```

### 多模型配置

如果你有多个端点，可以为不同的 Claude 模型映射不同的端点：

```bash
# 高性能模型用于复杂任务
BIG_MODEL="ep-xxxxxxxxxx-xxxxx"

# 中等性能模型用于一般任务
MIDDLE_MODEL="ep-20250723142408-abc12"

# 快速模型用于简单任务
SMALL_MODEL="ep-20250723142409-def34"
```

## 测试连接

### 使用测试脚本

```bash
python test_ark.py
```

### 手动测试

使用 curl 测试代理：

```bash
# 基本对话测试
curl -X POST http://localhost:8082/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "messages": [
      {
        "role": "user",
        "content": "你好，请用中文自我介绍"
      }
    ],
    "max_tokens": 500
  }'
```

### 使用原生 ARK SDK 测试

验证 ARK API 直接访问：

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://ark-cn-beijing.bytedance.net/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

completion = client.chat.completions.create(
    model="ep-xxxxxxxxxx-xxxxx",  # 你的端点 ID
    messages=[
        {"role": "system", "content": "你是人工智能助手"},
        {"role": "user", "content": "你好"},
    ],
)
print(completion.choices[0].message.content)
```

## 与 Claude Code 集成

### 配置 Claude Code

```bash
# 设置 Anthropic API Key（任意值）
export ANTHROPIC_API_KEY="test-key"

# 设置代理地址
export ANTHROPIC_BASE_URL="http://localhost:8082"

# 使用 Claude Code
claude "你好，请用中文回答问题"
```

### 模型映射关系

| Claude Code 请求模型 | 映射到环境变量 | ARK 端点 |
|---------------------|----------------|----------|
| `claude-3-5-haiku-*` | `SMALL_MODEL` | 你配置的快速端点 |
| `claude-3-5-sonnet-*` | `MIDDLE_MODEL` | 你配置的标准端点 |
| `claude-3-opus-*` | `BIG_MODEL` | 你配置的高性能端点 |

### 验证集成

```bash
# 测试基本对话
claude "介绍一下北京的天气"

# 测试代码生成
claude "写一个 Python 函数来计算斐波那契数列"

# 测试中文对话
claude "请用中文解释什么是机器学习"
```

## 支持的功能

### ✅ 完全支持的功能

- **文本对话**: 基础对话和复杂推理
- **流式响应**: 实时获取生成内容
- **系统提示**: 自定义 AI 助手行为
- **多轮对话**: 保持上下文的连续对话
- **参数控制**: temperature, top_p, max_tokens 等
- **停止词**: 自定义停止生成的词汇

### ⚠️ 限制和注意事项

- **多模态**: ARK API 的多模态支持取决于你选择的模型端点
- **工具调用**: 需要端点支持 function calling
- **文件上传**: 限制取决于 ARK 服务的具体实现

### 🔧 配置示例

```python
# 通过代理使用 ARK API 的完整示例
import requests

response = requests.post(
    "http://localhost:8082/v1/messages",
    headers={
        "x-api-key": "test-key",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    },
    json={
        "model": "claude-3-5-sonnet-20241022",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的技术助手，请用中文回答问题。"
            },
            {
                "role": "user", 
                "content": "解释一下什么是 REST API"
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
        "stream": False
    }
)

print(response.json())
```

## 故障排查

### 常见问题

#### 1. API Key 无效

**症状**: `401 Unauthorized` 错误

**解决方案**:
```bash
# 检查 API Key 是否正确设置
echo $ARK_API_KEY

# 验证 API Key 格式和有效性
# ARK API Key 通常不以 'sk-' 开头
```

#### 2. 端点 ID 错误

**症状**: `404 Not Found` 或模型相关错误

**解决方案**:
```bash
# 检查端点 ID 格式
echo $BIG_MODEL
# 应该是类似: ep-xxxxxxxxxx-xxxxx

# 在 ARK 控制台验证端点 ID 是否存在和活跃
```

#### 3. 网络连接问题

**症状**: 连接超时或网络错误

**解决方案**:
```bash
# 测试网络连接
curl -I https://ark-cn-beijing.bytedance.net/api/v3

# 检查防火墙和代理设置
```

#### 4. 代理服务器启动失败

**症状**: 端口被占用或配置错误

**解决方案**:
```bash
# 检查端口是否被占用
lsof -i :8082

# 更改端口
export PORT=8083

# 查看详细日志
export LOG_LEVEL=DEBUG
uv run python -m src.main
```

### 调试技巧

#### 启用详细日志

```bash
export LOG_LEVEL=DEBUG
uv run python -m src.main
```

#### 检查配置

```bash
# 验证环境变量
env | grep -E "(ARK_|OPENAI_|BIG_|MIDDLE_|SMALL_)"

# 测试配置加载
python -c "from src.core.config import config; print(f'API Key: {config.api_key[:10]}...', f'Base URL: {config.openai_base_url}')"
```

#### 网络调试

```bash
# 测试代理健康状态
curl http://localhost:8082/health

# 查看代理信息
curl http://localhost:8082/v1/models
```

## API 特性对比

| 功能 | OpenAI API | ByteDance 搜索 API | ARK API |
|------|------------|-------------------|---------|
| 基础对话 | ✅ | ✅ | ✅ |
| 流式响应 | ✅ | ✅ | ✅ |
| 系统提示 | ✅ | ✅ | ✅ |
| 图像识别 | ✅ | ✅ | 取决于端点 |
| 文档分析 | ✅ | ✅ | 取决于端点 |
| 工具调用 | ✅ | ✅ | 取决于端点 |
| 代码执行 | ❌ | ✅ | 取决于端点 |
| 联网搜索 | ❌ | ✅ | 取决于端点 |
| 认证方式 | API Key | API Key + Headers | API Key |
| 特殊配置 | 无 | X-TT-LOGID | 无 |

## 最佳实践

### 1. 安全配置

```bash
# 使用环境变量而不是硬编码
export ARK_API_KEY="your-actual-key"

# 限制客户端访问
export ANTHROPIC_API_KEY="secure-client-key"

# 配置适当的超时
export REQUEST_TIMEOUT="60"
```

### 2. 性能优化

```bash
# 根据使用场景配置不同模型
BIG_MODEL="ep-high-performance-model"    # 复杂任务
MIDDLE_MODEL="ep-balanced-model"         # 一般任务  
SMALL_MODEL="ep-fast-model"              # 简单任务

# 调整令牌限制
MAX_TOKENS_LIMIT="4096"
MIN_TOKENS_LIMIT="100"
```

### 3. 监控和日志

```bash
# 生产环境建议使用 INFO 级别
LOG_LEVEL="INFO"

# 开发和调试使用 DEBUG 级别
LOG_LEVEL="DEBUG"
```

### 4. 容错配置

```bash
# 配置重试
MAX_RETRIES="3"

# 适当的超时设置
REQUEST_TIMEOUT="90"
```

## 总结

通过本指南，你应该能够成功配置并使用 ARK API 与 claude-code-proxy。ARK API 提供了高质量的中文 AI 服务，特别适合需要中文对话能力的应用场景。

如果遇到问题，请参考故障排查部分，或查看项目的 GitHub Issues 页面寻求帮助。

---

**相关文档**:
- [README.md](./README.md) - 项目总体介绍
- [QUICKSTART.md](./QUICKSTART.md) - 快速开始指南
- [BYTEDANCE_SETUP.md](./BYTEDANCE_SETUP.md) - ByteDance API 配置指南