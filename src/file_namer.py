"""
文件命名模块 - 使用LLM根据markdown内容生成文件名
"""

from typing import Annotated
import re
from openai import OpenAI


def generate_filename(
    content: Annotated[str, "markdown内容"],
    api_key: Annotated[str, "DeepSeek API密钥"],
    model: Annotated[str, "模型名称"] = "deepseek-chat",
    max_length: Annotated[int, "文件名最大长度"] = 50
) -> Annotated[str, "生成的文件名（不含扩展名）"]:
    """
    使用LLM根据markdown内容生成合适的文件名

    功能说明：
    - 调用DeepSeek API分析内容并生成简短的英文文件名
    - 确保文件名只包含小写字母、数字和下划线
    - 长度不超过指定限制
    - 如果生成失败，返回默认文件名

    参数：
        content: markdown内容（通常取前1000字符即可）
        api_key: DeepSeek API密钥
        model: 使用的模型名称
        max_length: 文件名最大长度，默认50

    返回：
        生成的文件名（不含.md扩展名）
    """
    # 取内容的前1000字符用于分析（节省token）
    sample_content = content[:1000] if len(content) > 1000 else content

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    system_prompt = f"""你是一个文件命名专家。根据提供的markdown内容，生成一个简短、准确的英文文件名。

要求：
1. 只使用小写字母（a-z）、数字（0-9）和下划线（_）
2. 长度不超过{max_length}个字符
3. 文件名应该简洁地反映内容主题
4. 不要包含文件扩展名
5. 只返回文件名本身，不要任何解释或其他文字

示例：
- machine_learning_basics
- python_web_scraping_guide
- react_hooks_tutorial"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请为以下内容生成文件名：\n\n{sample_content}"}
            ],
            stream=False
        )

        filename = response.choices[0].message.content.strip()

        # 清理文件名，确保符合要求
        filename = sanitize_filename(filename, max_length)

        return filename if filename else "untitled_document"

    except Exception as e:
        print(f"LLM生成文件名失败: {str(e)}")
        return "untitled_document"


def sanitize_filename(
    filename: Annotated[str, "原始文件名"],
    max_length: Annotated[int, "最大长度"] = 50
) -> Annotated[str, "清理后的文件名"]:
    """
    清理文件名，确保符合命名规范

    功能说明：
    - 转换为小写
    - 只保留字母、数字和下划线
    - 移除连续的下划线
    - 限制长度
    - 确保不以数字或下划线开头

    参数：
        filename: 原始文件名
        max_length: 最大长度限制

    返回：
        清理后的文件名
    """
    # 转换为小写
    filename = filename.lower()

    # 只保留字母、数字和下划线
    filename = re.sub(r'[^a-z0-9_]', '_', filename)

    # 移除连续的下划线
    filename = re.sub(r'_+', '_', filename)

    # 移除首尾的下划线
    filename = filename.strip('_')

    # 确保不以数字开头
    if filename and filename[0].isdigit():
        filename = 'doc_' + filename

    # 限制长度
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip('_')

    # 如果为空，返回默认值
    if not filename:
        filename = "untitled"

    return filename


def ensure_unique_filename(
    filename: Annotated[str, "基础文件名"],
    existing_files: Annotated[set, "已存在的文件名集合"]
) -> Annotated[str, "唯一的文件名"]:
    """
    确保文件名唯一，如有冲突则添加数字后缀

    功能说明：
    - 检查文件名是否已存在
    - 如果存在，添加数字后缀（_1, _2, _3...）
    - 返回唯一的文件名

    参数：
        filename: 基础文件名（不含扩展名）
        existing_files: 已存在的文件名集合

    返回：
        唯一的文件名（不含扩展名）
    """
    if filename not in existing_files:
        return filename

    # 添加数字后缀
    counter = 1
    while f"{filename}_{counter}" in existing_files:
        counter += 1

    return f"{filename}_{counter}"
