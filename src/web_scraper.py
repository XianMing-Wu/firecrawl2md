"""
网页爬取模块 - 使用Firecrawl API爬取网页内容
"""

from typing import Annotated, Dict, List, Optional
from firecrawl import Firecrawl
import time


def scrape_url(
    url: Annotated[str, "目标URL"],
    api_key: Annotated[str, "Firecrawl API密钥"],
    max_retries: Annotated[int, "最大重试次数"] = 3
) -> Annotated[Optional[Dict], "爬取结果字典，失败返回None"]:
    """
    使用Firecrawl爬取单个URL的内容

    功能说明：
    - 使用Firecrawl API获取网页的markdown格式内容
    - 自动重试失败的请求（最多重试3次）
    - 返回包含markdown内容和元数据的字典

    参数：
        url: 要爬取的网页URL
        api_key: Firecrawl API密钥
        max_retries: 最大重试次数，默认3次

    返回：
        成功返回包含以下字段的字典：
        - markdown: 网页的markdown格式内容
        - metadata: 网页元数据（标题、描述等）
        - url: 原始URL
        失败返回None

    异常：
        不抛出异常，失败时记录错误并返回None
    """
    firecrawl = Firecrawl(api_key=api_key)

    for attempt in range(max_retries):
        try:
            # 使用scrape方法获取markdown格式内容
            result = firecrawl.scrape(url, formats=["markdown"])

            # Firecrawl v2 API 直接返回数据对象，不是嵌套在 "data" 中
            if result:
                # 检查是否有 markdown 内容
                markdown_content = ""
                if hasattr(result, 'markdown'):
                    markdown_content = result.markdown
                elif isinstance(result, dict):
                    markdown_content = result.get("markdown", "")

                # 检查是否有 metadata
                metadata = {}
                if hasattr(result, 'metadata'):
                    metadata = result.metadata
                elif isinstance(result, dict):
                    metadata = result.get("metadata", {})

                if markdown_content:
                    return {
                        "markdown": markdown_content,
                        "metadata": metadata,
                        "url": url
                    }
                else:
                    print(f"警告: URL {url} 返回空内容")
                    print(f"返回数据类型: {type(result)}")
                    print(f"返回数据: {result}")
                    return None
            else:
                print(f"警告: URL {url} 返回空内容")
                return None

        except Exception as e:
            print(f"爬取URL失败 (尝试 {attempt + 1}/{max_retries}): {url}")
            print(f"错误: {str(e)}")

            if attempt < max_retries - 1:
                # 等待后重试
                time.sleep(2 ** attempt)  # 指数退避
            else:
                print(f"最终失败: {url}")
                return None

    return None


def scrape_urls(
    urls: Annotated[List[str], "URL列表"],
    api_key: Annotated[str, "Firecrawl API密钥"],
    delay: Annotated[float, "请求间隔（秒）"] = 1.0
) -> Annotated[List[Dict], "成功爬取的结果列表"]:
    """
    批量爬取多个URL的内容

    功能说明：
    - 遍历URL列表，逐个爬取内容
    - 在请求之间添加延迟，避免触发限流
    - 跳过失败的URL，继续处理剩余URL
    - 显示进度信息

    参数：
        urls: 要爬取的URL列表
        api_key: Firecrawl API密钥
        delay: 请求之间的延迟秒数，默认1秒

    返回：
        成功爬取的结果列表，每个元素是scrape_url返回的字典
    """
    results = []
    total = len(urls)

    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{total}] 正在爬取: {url}")

        result = scrape_url(url, api_key)

        if result:
            results.append(result)
            print(f"✓ 成功爬取")
        else:
            print(f"✗ 爬取失败，跳过")

        # 添加延迟（最后一个URL不需要延迟）
        if idx < total:
            time.sleep(delay)

    print(f"\n爬取完成: 成功 {len(results)}/{total}")
    return results
