# Firecrawl2MD

一个自动化工具，使用 Firecrawl 爬取网页内容，通过 DeepSeek AI 修复和优化 Markdown 格式，自动下载图片并生成规范的文档。

## 功能特性

- **智能爬取**: 使用 Firecrawl API 获取网页的主要内容（不包含导航栏等）
- **AI 修复**: 使用 DeepSeek LLM 分块修复 Markdown 格式问题
  - 自动修正标题层级关系
  - 规范化数学公式语法（行内公式 `$ $`，行间公式 `$$ $$`）
  - 修复代码块格式（添加语言标识）
  - 优化表格格式
  - 规范图片和链接语法
- **智能命名**: AI 根据内容生成简洁的英文文件名
- **图片管理**: 自动下载所有图片并替换为本地相对路径
- **动态分块**: 支持大文档智能分块处理（最大 32k tokens/块）

## 项目结构

```
firecrawl2md/
├── .env                 # API 密钥配置（需手动创建）
├── .env.example         # 环境变量示例
├── .gitignore          # Git 忽略文件
├── README.md           # 项目说明文档
├── requirements.txt    # Python 依赖
├── input.txt           # 输入 URL 列表（每行一个 URL）
├── output/             # 输出目录
│   ├── *.md           # 生成的 Markdown 文件
│   └── images/        # 下载的图片
│       └── {filename}/  # 按文档名分组的图片
└── src/
    ├── __init__.py
    ├── url_loader.py          # URL 加载模块
    ├── web_scraper.py         # 网页爬取模块
    ├── markdown_processor.py  # Markdown 处理模块
    ├── file_namer.py          # 文件命名模块
    ├── image_handler.py       # 图片处理模块
    └── main.py               # 主程序入口
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.8 或更高版本，以及 uv 包管理器。

```bash
# 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone <repository-url>
cd firecrawl2md
```

### 2. 安装依赖

```bash
# 使用 uv 安装依赖
uv pip install -r requirements.txt

# 或使用传统 pip
pip install -r requirements.txt
```

### 3. 配置 API 密钥

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Firecrawl API Key (获取地址: https://firecrawl.dev)
FIRECRAWL_API_KEY=fc-YOUR-API-KEY

# DeepSeek API Key (获取地址: https://platform.deepseek.com)
DEEPSEEK_API_KEY=sk-YOUR-API-KEY
```

### 4. 准备 URL 列表

在项目根目录创建 `input.txt` 文件，每行添加一个要爬取的 URL：

```
https://example.com/article1
https://example.com/article2
https://example.com/article3
```

### 5. 运行程序

```bash
cd src
python main.py
```

## 使用示例

### 基础用法

```bash
# 处理 input.txt 中的所有 URL
cd src
python main.py
```

### 程序执行流程

1. **加载环境变量**: 读取 API 密钥
2. **读取 URL 列表**: 从 `input.txt` 加载并验证 URL
3. **爬取网页内容**: 使用 Firecrawl 获取 Markdown 格式内容
4. **修复 Markdown**:
   - 智能分块（每块最大 32k tokens）
   - 使用 DeepSeek AI 修复每个分块
   - 合并修复后的内容
5. **生成文件名**: AI 分析内容生成简洁的英文文件名
6. **处理图片**:
   - 提取所有图片 URL
   - 下载到 `output/images/{filename}/` 目录
   - 替换为相对路径引用
7. **保存文件**: 输出到 `output/` 目录

### 输出示例

```
output/
├── python_web_scraping_guide.md
├── machine_learning_basics.md
└── images/
    ├── python_web_scraping_guide/
    │   ├── 1.jpg
    │   └── 2.png
    └── machine_learning_basics/
        ├── 1.jpg
        ├── 2.jpg
        └── 3.png
```

## 模块说明

### url_loader.py
负责从 `input.txt` 读取 URL 列表，并进行基础验证。

### web_scraper.py
使用 Firecrawl API 爬取网页内容，支持自动重试和错误处理。

### markdown_processor.py
最核心的模块，实现：
- Token 计数（使用 tiktoken）
- 动态分块算法（按 Markdown 标题分块）
- DeepSeek API 调用进行格式修复

### file_namer.py
使用 DeepSeek AI 分析文档内容，生成符合规范的文件名：
- 只包含小写字母、数字和下划线
- 长度限制 50 字符
- 自动处理重名冲突

### image_handler.py
处理 Markdown 中的图片：
- 正则提取图片 URL
- 批量下载图片
- 替换为相对路径引用
- 支持多种图片格式（jpg, png, gif, webp, svg）

### main.py
主程序入口，协调所有模块完成完整流程。

## API 使用说明

### Firecrawl API
- **用途**: 爬取网页内容，转换为 Markdown
- **获取**: https://firecrawl.dev
- **文档**: https://docs.firecrawl.dev

### DeepSeek API
- **用途**: AI 修复 Markdown 格式，生成文件名
- **获取**: https://platform.deepseek.com
- **模型**: deepseek-chat
- **API 兼容**: OpenAI API 格式

## 技术特点

### 类型安全
所有函数使用完整的类型注解和 `Annotated` 说明：

```python
def load_urls(
    file_path: Annotated[str, "输入文件路径"]
) -> Annotated[List[str], "URL列表"]:
    """从指定文件加载URL列表"""
    pass
```

### 模块解耦
每个模块职责单一，接口清晰，便于维护和测试。

### 错误处理
- 网络请求失败自动重试（指数退避）
- API 调用失败降级处理
- 详细的日志输出

### 性能优化
- 支持大文档动态分块
- 图片流式下载
- 批量处理优化

## 常见问题

### 1. API 密钥错误

确保 `.env` 文件格式正确，密钥有效。

### 2. 图片下载失败

部分图片可能因防盗链或网络问题无法下载，程序会保留原始链接并继续处理。

### 3. Markdown 修复质量

DeepSeek AI 的修复质量取决于原始内容质量。如需调整修复策略，可修改 `markdown_processor.py` 中的 prompt。

### 4. 分块大小调整

默认每块最大 32k tokens，可在调用 `fix_markdown()` 时修改 `max_tokens` 参数。

## 依赖说明

- **firecrawl-py**: Firecrawl 官方 Python SDK
- **openai**: OpenAI SDK（DeepSeek API 兼容）
- **python-dotenv**: 环境变量管理
- **tiktoken**: Token 计数工具
- **requests**: HTTP 请求库

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2025-10-26)
- 初始版本发布
- 实现核心功能：爬取、修复、命名、图片处理
