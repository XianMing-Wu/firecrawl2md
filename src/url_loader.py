"""
URL加载模块 - 从input.txt读取URL列表
"""

from typing import Annotated, List
from pathlib import Path


def load_urls(file_path: Annotated[str, "输入文件路径"]) -> Annotated[List[str], "URL列表"]:
    """
    从指定文件加载URL列表

    功能说明：
    - 读取文件中的每一行
    - 过滤空行和纯空格行
    - 去除每行首尾空白字符
    - 返回有效的URL列表

    参数：
        file_path: 包含URL的文本文件路径

    返回：
        包含所有有效URL的列表

    异常：
        FileNotFoundError: 当文件不存在时抛出
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    urls = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # 跳过空行
                urls.append(line)

    return urls


def validate_url(url: Annotated[str, "待验证的URL"]) -> Annotated[bool, "URL是否有效"]:
    """
    简单验证URL格式是否有效

    功能说明：
    - 检查URL是否以http://或https://开头

    参数：
        url: 待验证的URL字符串

    返回：
        True表示URL格式有效，False表示无效
    """
    return url.startswith(('http://', 'https://'))
