# 多API密钥模型映射功能

这个功能允许你为不同的 `ANTHROPIC_API_KEY` 配置不同的模型，实现多租户模型分级。

## 功能概述

- **单密钥模式**：保持现有的 `ANTHROPIC_API_KEY` 单一验证模式（向后兼容）
- **多密钥模式**：支持多个 API 密钥，每个密钥可以映射到不同的模型配置
- **自动回退**：如果某个 API 密钥没有特定配置，自动使用默认模型

## 配置方式

### 环境变量格式

```bash
# 多API密钥配置格式
API_KEY_MODEL_MAPPING_<KEY_ID>_API_KEY="实际的API密钥"
API_KEY_MODEL_MAPPING_<KEY_ID>_BIG="对应的大模型"
API_KEY_MODEL_MAPPING_<KEY_ID>_MIDDLE="对应的中等模型"
API_KEY_MODEL_MAPPING_<KEY_ID>_SMALL="对应的小模型"
API_KEY_MODEL_MAPPING_<KEY_ID>_IGNORE_TEMPERATURE="true/false"  # 是否忽略temperature参数
```

### 配置示例

```bash
# 基础默认配置
OPENAI_API_KEY="your-openai-api-key"
BIG_MODEL="gpt-4o"
MIDDLE_MODEL="gpt-4o"
SMALL_MODEL="gpt-4o-mini"

# 高级用户配置（使用最好的模型）
API_KEY_MODEL_MAPPING_PREMIUM_API_KEY="claude-premium-user-key"
API_KEY_MODEL_MAPPING_PREMIUM_BIG="gpt-4o"
API_KEY_MODEL_MAPPING_PREMIUM_MIDDLE="gpt-4o"
API_KEY_MODEL_MAPPING_PREMIUM_SMALL="gpt-4o-mini"

# 标准用户配置（使用平衡的模型）
API_KEY_MODEL_MAPPING_STANDARD_API_KEY="claude-standard-user-key"
API_KEY_MODEL_MAPPING_STANDARD_BIG="gpt-4o-mini"
API_KEY_MODEL_MAPPING_STANDARD_MIDDLE="gpt-4o-mini"
API_KEY_MODEL_MAPPING_STANDARD_SMALL="gpt-3.5-turbo"

# 基础用户配置（使用经济型模型）
API_KEY_MODEL_MAPPING_BASIC_API_KEY="claude-basic-user-key"
API_KEY_MODEL_MAPPING_BASIC_BIG="gpt-3.5-turbo"
API_KEY_MODEL_MAPPING_BASIC_MIDDLE="gpt-3.5-turbo"
API_KEY_MODEL_MAPPING_BASIC_SMALL="gpt-3.5-turbo"
```

## 模型映射规则

| Claude 模型请求 | 映射到的配置 | 说明 |
|----------------|-------------|------|
| `claude-3-opus-*` | `BIG_MODEL` | 最高性能模型 |
| `claude-3-5-sonnet-*` | `MIDDLE_MODEL` | 中等性能模型 |
| `claude-3-haiku-*` | `SMALL_MODEL` | 快速响应模型 |
| 其他未知模型 | `BIG_MODEL` | 默认使用大模型 |

## 使用场景

### 1. 多租户服务分级

```bash
# VIP用户 - 使用最好的模型
API_KEY_MODEL_MAPPING_VIP_API_KEY="vip-user-12345"
API_KEY_MODEL_MAPPING_VIP_BIG="gpt-4o"
API_KEY_MODEL_MAPPING_VIP_MIDDLE="gpt-4o"
API_KEY_MODEL_MAPPING_VIP_SMALL="gpt-4o"

# 普通用户 - 使用标准模型
API_KEY_MODEL_MAPPING_NORMAL_API_KEY="normal-user-67890"
API_KEY_MODEL_MAPPING_NORMAL_BIG="gpt-4o-mini"
API_KEY_MODEL_MAPPING_NORMAL_MIDDLE="gpt-4o-mini"
API_KEY_MODEL_MAPPING_NORMAL_SMALL="gpt-3.5-turbo"
```

### 2. 不同团队使用不同模型源

```bash
# 研发团队 - 使用 OpenAI 模型
API_KEY_MODEL_MAPPING_DEV_API_KEY="dev-team-key"
API_KEY_MODEL_MAPPING_DEV_BIG="gpt-4o"
API_KEY_MODEL_MAPPING_DEV_MIDDLE="gpt-4o"
API_KEY_MODEL_MAPPING_DEV_SMALL="gpt-4o-mini"

# 测试团队 - 使用 ARK 模型
API_KEY_MODEL_MAPPING_TEST_API_KEY="test-team-key"
API_KEY_MODEL_MAPPING_TEST_BIG="ep-high-performance"
API_KEY_MODEL_MAPPING_TEST_MIDDLE="ep-balanced"
API_KEY_MODEL_MAPPING_TEST_SMALL="ep-fast"
```

## 客户端使用

客户端使用不同的 API 密钥时，会自动获得对应的模型配置：

```bash
# 高级用户
export ANTHROPIC_API_KEY="claude-premium-user-key"
export ANTHROPIC_BASE_URL="http://localhost:8082"
claude "复杂的编程问题"  # 会使用 gpt-4o

# 基础用户
export ANTHROPIC_API_KEY="claude-basic-user-key"
export ANTHROPIC_BASE_URL="http://localhost:8082"  
claude "简单的问题"  # 会使用 gpt-3.5-turbo
```

## 向后兼容性

- 如果不配置多密钥映射，系统会继续使用原有的单密钥验证方式
- 现有的 `.env` 配置无需修改即可继续工作
- 如果某个 API 密钥没有特定配置，会自动回退到默认的 `BIG_MODEL`、`MIDDLE_MODEL`、`SMALL_MODEL`

## 验证配置

运行测试脚本验证配置是否正确：

```bash
uv run python test_multi_key.py
```

## 配置示例文件

参考 `.env.multi-key.example` 文件查看完整的配置示例。

## 日志记录

系统会自动记录以下信息，便于监控和调试：

### API 密钥认证日志
```
INFO - API Key authenticated: claude-pr...skey, Models: BIG=gpt-4o, MIDDLE=gpt-4o, SMALL=gpt-4o-mini, IgnoreTemp=false
```

### 模型映射日志
```
INFO - Model mapping: claude-3-5-sonnet-20241022 -> gpt-4o (type: MIDDLE, API: claude-pr...skey)
```

### Temperature 处理日志
```
INFO - Temperature ignored for API claude-ba...skey: 0.7 -> None
```

### 日志格式说明
- API 密钥在日志中会被部分遮蔽，只显示前8位和后4位，确保安全性
- 记录实际使用的模型映射，便于验证配置是否正确
- 当 temperature 被忽略时会记录原始值和处理结果

## 安全注意事项

1. **API 密钥安全**：确保所有 API 密钥都是安全的，定期轮换
2. **权限控制**：不同级别的用户应使用不同的 API 密钥
3. **监控使用**：建议监控不同密钥的使用情况，防止滥用
4. **成本控制**：根据用户级别合理配置模型，控制 API 调用成本
5. **日志安全**：API 密钥在日志中已自动遮蔽，但仍需注意日志文件的访问权限