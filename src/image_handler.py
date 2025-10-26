"""
图片处理模块 - 下载图片并替换markdown中的图片链接
"""

from typing import Annotated, List, Dict, Tuple
import re
import requests
from pathlib import Path
from urllib.parse import urlparse


def extract_image_urls(
    markdown_content: Annotated[str, "markdown内容"]
) -> Annotated[List[str], "图片URL列表"]:
    """
    从markdown内容中提取所有图片URL

    功能说明：
    - 使用正则表达式匹配markdown图片语法：![...](url)
    - 提取所有图片的URL
    - 保持URL的原始顺序

    参数：
        markdown_content: markdown格式的文本内容

    返回：
        按出现顺序排列的图片URL列表
    """
    # 匹配markdown图片语法：![alt](url)
    pattern = r'!\[.*?\]\((.*?)\)'
    matches = re.findall(pattern, markdown_content)

    return matches


def download_image(
    url: Annotated[str, "图片URL"],
    save_path: Annotated[str, "保存路径"],
    timeout: Annotated[int, "超时时间（秒）"] = 30
) -> Annotated[bool, "是否下载成功"]:
    """
    下载图片到指定路径

    功能说明：
    - 发送HTTP请求下载图片
    - 保存到指定的本地路径
    - 处理下载过程中的错误

    参数：
        url: 图片的URL地址
        save_path: 保存图片的本地路径
        timeout: 请求超时时间（秒）

    返回：
        True表示下载成功，False表示失败
    """
    try:
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()

        # 确保保存目录存在
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # 保存图片
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True

    except Exception as e:
        print(f"下载图片失败: {url}")
        print(f"错误: {str(e)}")
        return False


def get_image_extension(
    url: Annotated[str, "图片URL"]
) -> Annotated[str, "图片扩展名"]:
    """
    从URL中获取图片扩展名

    功能说明：
    - 解析URL路径，提取文件扩展名
    - 如果无法确定，默认返回.jpg

    参数：
        url: 图片URL

    返回：
        图片扩展名（包含点号，如.jpg）
    """
    parsed = urlparse(url)
    path = parsed.path
    ext = Path(path).suffix

    # 如果没有扩展名或扩展名不常见，默认使用.jpg
    if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
        ext = '.jpg'

    return ext


def process_images(
    markdown_content: Annotated[str, "markdown内容"],
    filename: Annotated[str, "markdown文件名（不含扩展名）"],
    output_dir: Annotated[str, "输出目录路径"]
) -> Annotated[str, "处理后的markdown内容"]:
    """
    下载markdown中的所有图片并替换为相对路径

    功能说明：
    - 提取markdown中的所有图片URL
    - 创建images/{filename}/目录
    - 按顺序下载图片并命名为1.jpg, 2.jpg等
    - 替换markdown中的图片链接为相对路径
    - 下载失败的图片保留原链接

    参数：
        markdown_content: 原始markdown内容
        filename: markdown文件名（用于创建图片子目录）
        output_dir: 输出根目录（通常是output/）

    返回：
        图片链接已替换为相对路径的markdown内容
    """
    # 提取所有图片URL
    image_urls = extract_image_urls(markdown_content)

    if not image_urls:
        print("未发现图片链接")
        return markdown_content

    print(f"发现 {len(image_urls)} 个图片")

    # 创建图片保存目录
    image_dir = Path(output_dir) / "images" / filename
    image_dir.mkdir(parents=True, exist_ok=True)

    # 下载图片并记录URL到本地路径的映射
    url_to_path: Dict[str, str] = {}

    for idx, url in enumerate(image_urls, 1):
        # 获取图片扩展名
        ext = get_image_extension(url)

        # 本地保存路径
        local_filename = f"{idx}{ext}"
        local_path = image_dir / local_filename

        print(f"  [{idx}/{len(image_urls)}] 下载图片: {url[:60]}...")

        # 下载图片
        if download_image(url, str(local_path)):
            # 相对于markdown文件的相对路径
            relative_path = f"./images/{filename}/{local_filename}"
            url_to_path[url] = relative_path
            print(f"  ✓ 保存为: {relative_path}")
        else:
            print(f"  ✗ 下载失败，保留原链接")

    # 替换markdown中的图片链接
    updated_content = markdown_content
    for original_url, new_path in url_to_path.items():
        # 使用正则替换，保留alt文本
        pattern = r'!\[(.*?)\]\(' + re.escape(original_url) + r'\)'
        replacement = r'![\1](' + new_path + ')'
        updated_content = re.sub(pattern, replacement, updated_content)

    print(f"✓ 成功下载 {len(url_to_path)}/{len(image_urls)} 个图片")

    return updated_content
