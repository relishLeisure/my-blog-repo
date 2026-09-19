import sys
from pathlib import Path
from datetime import datetime

def meets_condition(content: str) -> bool:
    """
    判断 Markdown 内容是否符合条件。
    如果返回 True，则跳过该文件；如果返回 False，则执行插入操作。
    
    【当前逻辑】：检查文件开头是否已经包含 '---' (即是否已经有 Front Matter)。
    你可以根据需要随意修改此函数的判断逻辑。
    """
    # 忽略前导空白字符后，判断是否以 --- 开头
    return content.lstrip().startswith('---')

def generate_front_matter(file_path: Path) -> str:
    """
    模拟 Hugo archetypes 模板逻辑，生成 Front Matter 字符串。
    """
    # 获取不带后缀的文件名 (例如: "my-first-post")
    base_name = file_path.stem 
    
    # 模拟 replace .File.ContentBaseName "-" " " | title 
    # 将连字符替换为空格，并将每个单词首字母大写
    title = base_name.replace("-", " ").title()
    
    # 模拟 {{ .Date }} 
    # 生成带时区的 ISO 8601 格式时间，例如: 2026-09-19T20:07:20+08:00
    date_str = datetime.now().astimezone().isoformat(timespec='seconds')
    
    # 构建 YAML 格式的 Front Matter
    front_matter = f"""---
title: "{title}"
date: {date_str}
draft: true
slug: "{base_name}"
categories: []
---

""" 
    return front_matter

def process_md_files(directory: str):
    folder_path = Path(directory)
    
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"错误: 路径 '{directory}' 不存在或不是文件夹！")
        return
        
    md_files = folder_path.rglob('*.md')
    modified_count = 0
    
    print(f"开始扫描目录: {folder_path.resolve()}")
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 判断是否符合条件
            if not meets_condition(content):
                # 生成模板文字
                new_meta = generate_front_matter(file_path)
                
                # 【在开头插入】
                new_content = new_meta + content
                
                # 如果你想【在结尾插入】，请注释掉上一行，并取消下面这行的注释：
                # new_content = content + "\n\n" + new_meta
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                print(f"已补全 Front Matter: {file_path.name}")
                modified_count += 1
                
        except Exception as e:
            print(f"处理文件 {file_path.name} 时出错: {e}")
            
    print(f"\n处理完成！共修改了 {modified_count} 个 .md 文件。")

if __name__ == "__main__":
    # 允许从命令行传入路径，如果没有传入则默认处理当前目录
    if len(sys.argv) > 1:
        TARGET_DIR = sys.argv[1]
    else:
        TARGET_DIR = '.' 
        
    process_md_files(TARGET_DIR)