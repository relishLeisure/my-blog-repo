import re
import sys
from pathlib import Path

def convert_h3_to_bold(directory):
    # 匹配 HTML 格式的 H3 标题: <h3>标题</h3>
    # <h3[^>]*> 处理可能带属性的 h3 标签 (例如 <h3 class="title">)
    # \s*(.*?)\s* 用于去除标题文字前后的多余空格，防止加粗语法失效 (如 ** 标题 ** 是无效的)
    html_h3_pattern = re.compile(r'<h3[^>]*>\s*(.*?)\s*</h3>', re.IGNORECASE)
    
    # 匹配 Markdown 原生格式的 H3 标题: ### 标题
    # ^ 匹配行首 (配合 re.MULTILINE 使用)
    # \s+ 匹配 ### 后面的空格
    md_h3_pattern = re.compile(r'^###\s+(.*?)\s*$', re.MULTILINE)
    
    # 获取目录下所有 .md 文件
    folder_path = Path(directory)
    md_files = folder_path.rglob('*.md')
    
    modified_count = 0
    
    print(f"开始扫描目录: {folder_path.resolve()}")
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 执行替换，r'**\1**' 中的 \1 代表正则表达式中括号 (.*?) 提取到的标题纯文本
            # 1. 先替换 HTML 标签的 H3
            new_content = html_h3_pattern.sub(r'**\1**', content)
            # 2. 再替换 Markdown 原生语法的 H3
            new_content = md_h3_pattern.sub(r'**\1**', new_content)
            
            # 如果内容发生了改变，再写入文件
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"已转换 H3 标题: {file_path}")
                modified_count += 1
                
        except Exception as e:
            print(f"读取或写入文件 {file_path} 时出错: {e}")
            
    print(f"\n处理完成！共修改了 {modified_count} 个 .md 文件。")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        TARGET_DIR = sys.argv[1]
    else:
        TARGET_DIR = '.'
    
    convert_h3_to_bold(TARGET_DIR)