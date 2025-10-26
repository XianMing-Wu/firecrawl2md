"""
主流程模块 - 协调所有模块完成网页转Markdown的完整流程
"""

import os
from typing import Annotated
from pathlib import Path
from dotenv import load_dotenv

from url_loader import load_urls, validate_url
from web_scraper import scrape_urls
from markdown_processor import fix_markdown
from file_namer import generate_filename, sanitize_filename, ensure_unique_filename
from image_handler import process_images


def main(
    input_file: Annotated[str, "输入文件路径"] = "input.txt",
    output_dir: Annotated[str, "输出目录路径"] = "output"
) -> Annotated[None, "无返回值"]:
    """
    主流程函数 - 完成从URL到Markdown文件的完整转换

    功能说明：
    1. 加载环境变量
    2. 读取input.txt中的URL列表
    3. 使用Firecrawl爬取每个URL的内容
    4. 使用LLM分块修复markdown内容
    5. 使用LLM生成文件名并重命名
    6. 下载图片并替换为相对路径
    7. 保存最终的markdown文件

    参数：
        input_file: 包含URL列表的输入文件路径
        output_dir: 输出markdown文件的目录路径

    返回：
        无返回值
    """
    print("=" * 60)
    print("Firecrawl2MD - 网页转Markdown工具")
    print("=" * 60)

    # 1. 加载环境变量
    print("\n[1/6] 加载环境变量...")
    load_dotenv()

    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

    if not firecrawl_api_key:
        print("错误: 未找到FIRECRAWL_API_KEY环境变量")
        print("请在.env文件中设置FIRECRAWL_API_KEY")
        return

    if not deepseek_api_key:
        print("错误: 未找到DEEPSEEK_API_KEY环境变量")
        print("请在.env文件中设置DEEPSEEK_API_KEY")
        return

    print("✓ API密钥加载成功")

    # 2. 读取URL列表
    print("\n[2/6] 读取URL列表...")
    try:
        urls = load_urls(input_file)
        print(f"✓ 加载了 {len(urls)} 个URL")

        # 验证URL格式
        valid_urls = [url for url in urls if validate_url(url)]
        invalid_count = len(urls) - len(valid_urls)

        if invalid_count > 0:
            print(f"警告: {invalid_count} 个URL格式无效，已跳过")

        if not valid_urls:
            print("错误: 没有有效的URL可处理")
            return

        urls = valid_urls

    except FileNotFoundError:
        print(f"错误: 未找到文件 {input_file}")
        print(f"请创建 {input_file} 文件并在每行添加一个URL")
        return

    # 3. 爬取网页内容
    print("\n[3/6] 爬取网页内容...")
    scraped_data = scrape_urls(urls, firecrawl_api_key)

    if not scraped_data:
        print("错误: 没有成功爬取任何网页")
        return

    # 4. 处理每个爬取的内容
    print("\n[4/6] 处理markdown内容...")

    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 跟踪已使用的文件名
    used_filenames = set()

    for idx, data in enumerate(scraped_data, 1):
        print(f"\n{'=' * 60}")
        print(f"处理文档 {idx}/{len(scraped_data)}")
        print(f"URL: {data['url']}")
        print(f"{'=' * 60}")

        markdown_content = data.get("markdown", "")

        if not markdown_content.strip():
            print("警告: 内容为空，跳过")
            continue

        # 4.1 修复markdown
        print("\n[4.1] 修复markdown格式...")
        fixed_markdown = fix_markdown(markdown_content, deepseek_api_key)

        # 4.2 生成文件名
        print("\n[4.2] 生成文件名...")
        filename = generate_filename(fixed_markdown, deepseek_api_key)
        filename = sanitize_filename(filename)
        filename = ensure_unique_filename(filename, used_filenames)
        used_filenames.add(filename)
        print(f"✓ 文件名: {filename}.md")

        # 4.3 处理图片
        print("\n[4.3] 处理图片...")
        final_markdown = process_images(fixed_markdown, filename, output_dir)

        # 4.4 保存文件
        print("\n[4.4] 保存文件...")
        output_file = output_path / f"{filename}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_markdown)

        print(f"✓ 已保存: {output_file}")

    # 5. 完成
    print("\n" + "=" * 60)
    print("处理完成!")
    print("=" * 60)
    print(f"成功处理: {len(scraped_data)} 个文档")
    print(f"输出目录: {output_path.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    """
    程序入口点

    功能说明：
    - 执行主流程
    - 捕获并显示任何未处理的异常
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        print(f"\n\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
