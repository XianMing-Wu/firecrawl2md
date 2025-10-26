"""
Markdown处理模块 - 分块和LLM修复markdown内容
"""

from typing import Annotated, List
import re
import tiktoken
from openai import OpenAI


def count_tokens(
    text: Annotated[str, "待计数的文本"],
    model: Annotated[str, "模型名称"] = "gpt-3.5-turbo"
) -> Annotated[int, "token数量"]:
    """
    计算文本的token数量

    功能说明：
    - 使用tiktoken库计算文本的token数
    - 支持不同的模型编码方式

    参数：
        text: 待计数的文本内容
        model: 模型名称，用于选择编码器

    返回：
        文本的token数量
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def chunk_markdown(
    content: Annotated[str, "markdown内容"],
    max_tokens: Annotated[int, "每块最大token数"] = 2048
) -> Annotated[List[str], "分块后的markdown列表"]:
    """
    将markdown内容按标题动态分块

    功能说明：
    - 识别所有markdown标题（#, ##, ###, ####）
    - 每个分块以标题开头，在下一个标题前结束
    - 每个分块尽可能接近max_tokens但不超过
    - 如果单个标题块超过max_tokens，则强制切分

    参数：
        content: 原始markdown内容
        max_tokens: 每块最大token数，默认32000

    返回：
        分块后的markdown内容列表
    """
    if not content.strip():
        return []

    # 如果内容本身不超过限制，直接返回
    if count_tokens(content) <= max_tokens:
        return [content]

    lines = content.split('\n')
    chunks = []
    current_chunk = []
    current_tokens = 0

    # 正则匹配markdown标题
    heading_pattern = re.compile(r'^(#{1,4})\s+')

    i = 0
    while i < len(lines):
        line = lines[i]
        line_tokens = count_tokens(line + '\n')

        # 检查是否是标题行
        is_heading = heading_pattern.match(line)

        if is_heading and current_chunk:
            # 遇到新标题，检查当前块是否需要保存
            if current_tokens > 0:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0

        # 添加当前行到当前块
        current_chunk.append(line)
        current_tokens += line_tokens

        # 检查是否超过限制
        if current_tokens >= max_tokens:
            # 查找下一个标题作为切分点
            next_heading_idx = None
            for j in range(i + 1, len(lines)):
                if heading_pattern.match(lines[j]):
                    next_heading_idx = j
                    break

            if next_heading_idx:
                # 在下一个标题前切分
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            else:
                # 没有更多标题，保存当前块
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0

        i += 1

    # 保存最后一个块
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks


def fix_markdown_chunk(
    chunk: Annotated[str, "markdown分块内容"],
    api_key: Annotated[str, "DeepSeek API密钥"],
    model: Annotated[str, "模型名称"] = "deepseek-chat"
) -> Annotated[str, "修复后的markdown内容"]:
    """
    使用LLM修复单个markdown分块

    功能说明：
    - 调用DeepSeek API修复markdown格式问题
    - 确保标题层级正确
    - 修复公式、代码块、表格、图片、链接格式

    参数：
        chunk: 待修复的markdown分块
        api_key: DeepSeek API密钥
        model: 使用的模型名称

    返回：
        修复后的markdown内容
    """
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    system_prompt = """你是一个Markdown文档修复专家。请修复以下markdown内容：

修复要点：
1. 确保层级关系准确（#/##/###/####的层级关系正确）
2. 行内公式和变量使用 $ ... $ 包裹，行间公式使用 $$ ... $$ 包裹
3. 代码块使用 ```language 包裹，确保language标识正确
4. 表格使用正确的markdown语法（| ... | ... |，对齐使用 :-: 或 :-- 或 --:）
5. 图片使用 ![alt](url) 格式
6. 链接使用 [title](url) 格式

重要：只返回修复后的markdown内容，不要添加任何解释或说明文字。"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk}
            ],
            stream=False
        )

        fixed_content = response.choices[0].message.content
        return fixed_content if fixed_content else chunk

    except Exception as e:
        print(f"LLM修复失败: {str(e)}")
        print("返回原始内容")
        return chunk


def fix_markdown(
    content: Annotated[str, "markdown内容"],
    api_key: Annotated[str, "DeepSeek API密钥"],
    max_tokens: Annotated[int, "每块最大token数"] = 2048
) -> Annotated[str, "修复后的完整markdown内容"]:
    """
    修复完整的markdown文档

    功能说明：
    - 将markdown内容分块
    - 逐块调用LLM修复
    - 合并修复后的内容
    - 显示进度信息

    参数：
        content: 原始markdown内容
        api_key: DeepSeek API密钥
        max_tokens: 每块最大token数

    返回：
        修复后的完整markdown内容
    """
    if not content.strip():
        return content

    # 分块
    chunks = chunk_markdown(content, max_tokens)
    print(f"Markdown内容已分为 {len(chunks)} 块")

    # 逐块修复
    fixed_chunks = []
    for idx, chunk in enumerate(chunks, 1):
        print(f"正在修复第 {idx}/{len(chunks)} 块...")
        fixed_chunk = fix_markdown_chunk(chunk, api_key)
        fixed_chunks.append(fixed_chunk)

    # 合并
    fixed_content = '\n\n'.join(fixed_chunks)
    print("✓ Markdown修复完成")

    return fixed_content
