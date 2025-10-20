# 代码分析AI Agent

这是一个能够接收代码和需求描述，分析代码结构并生成结构化分析报告的AI Agent服务。采用模块化架构设计，代码结构清晰，易于维护和扩展。

## 项目结构

```
f:\new\
├── app/                      # 主应用目录
│   ├── api/                  # API路由模块
│   │   ├── __init__.py
│   │   ├── analysis_routes.py  # 分析相关端点
│   │   └── health_routes.py    # 健康检查和根路径端点
│   ├── core/                 # 核心业务逻辑
│   │   ├── __init__.py
│   │   └── code_analyzer.py    # 代码分析器
│   ├── schemas/              # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py          # 所有数据模型定义
│   ├── utils/                # 工具函数
│   │   ├── __init__.py
│   │   └── file_utils.py       # 文件处理工具
│   └── main.py               # 主应用配置
├── server.py                 # 应用入口点
├── requirements.txt          # Python依赖
├── Dockerfile                # Docker配置
├── .env                      # 环境变量
├── .env.example              # 环境变量示例
├── README.md                 # 项目文档
└── test_client.py            # 测试客户端
```

## 功能特性

### 核心功能
- 接收multipart/form-data请求，包含需求描述和代码压缩包
- 自动解压并分析代码结构
- 提取代码中的函数和关键实现
- 根据需求描述生成功能实现定位报告
- 提供项目执行计划建议

### 加分功能
- 动态生成针对特定项目的测试代码
- 模拟功能验证并提供结果报告

## API接口

### 1. 基础代码分析

**端点:** `POST /analyze`

**请求格式:** `multipart/form-data`

**参数:**
- `problem_description` (string): 项目功能需求描述
- `code_zip` (file): 包含完整源代码的ZIP文件

**响应格式:** JSON

### 2. 代码分析与功能验证

**端点:** `POST /analyze-with-verification`

**请求格式:** `multipart/form-data`

**参数:**
- `problem_description` (string): 项目功能需求描述
- `code_zip` (file): 包含完整源代码的ZIP文件

**响应格式:** JSON，包含基础分析结果和功能验证信息

### 3. 健康检查

**端点:** `GET /health`

**响应:** `{"status": "healthy"}`

## 快速开始

### 使用Docker运行（推荐）

1. 确保已安装Docker

2. 构建Docker镜像
```bash
docker build -t code-analysis-agent .
```

3. 运行容器
```bash
docker run -p 8000:8000 code-analysis-agent
```

4. 服务将在 http://localhost:8000 启动

### 直接运行Python代码

1. 确保Python 3.8+已安装

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动服务
```bash
python server.py
```

## API文档

服务启动后，可以访问以下地址查看自动生成的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 报告格式说明

### 基础分析报告格式
```json
{
  "feature_analysis": [
    {
      "feature_description": "功能描述",
      "implementation_location": [
        {
          "file": "文件路径",
          "function": "函数名",
          "lines": "行号范围"
        }
      ]
    }
  ],
  "execution_plan_suggestion": "执行计划建议"
}
```

### 包含功能验证的报告格式
```json
{
  "feature_analysis": [...],
  "execution_plan_suggestion": "...",
  "functional_verification": {
    "generated_test_code": "生成的测试代码",
    "execution_result": {
      "tests_passed": true/false,
      "log": "测试执行日志"
    }
  }
}
```

## 支持的编程语言

目前支持分析以下编程语言的代码：
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- TypeScript JSX (.tsx)
- JavaScript JSX (.jsx)
- Java (.java)
- C++ (.cpp)
- C# (.cs)

## 技术栈

- **框架**: FastAPI
- **语言**: Python 3.9
- **容器化**: Docker
- **数据验证**: Pydantic
- **环境配置**: python-dotenv
- **API文档**: 自动生成的Swagger UI和ReDoc

## 环境变量配置

可以通过`.env`文件或环境变量配置以下参数：
- `APP_HOST`: 应用监听地址（默认：0.0.0.0）
- `APP_PORT`: 应用监听端口（默认：8000）
- `APP_ENV`: 应用环境（development/production，默认：production）
- `LOG_LEVEL`: 日志级别（DEBUG/INFO/WARNING/ERROR，默认：INFO）
- `MAX_FILE_SIZE`: 最大文件大小（字节，默认：100MB）

## 注意事项

1. 上传的ZIP文件大小不应超过100MB
2. 代码分析基于静态分析，可能无法捕获所有动态生成的功能
3. 功能验证目前是模拟实现，在生产环境中需要进一步开发实际的测试执行功能

## 扩展与优化方向

1. 集成更先进的代码分析工具（如AST解析）
2. 实现实际的测试代码执行功能
3. 添加机器学习模型以提高功能识别准确性
4. 支持更多的编程语言和框架
5. 优化大型代码库的分析性能
6. 添加缓存机制以提高频繁请求的响应速度
7. 实现更细粒度的权限控制和API限流

## License

MIT