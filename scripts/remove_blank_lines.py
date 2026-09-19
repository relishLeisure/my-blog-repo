import re
import sys
from pathlib import Path

def compress_blank_lines(directory):
    # 匹配 2 个或更多连续换行符（即两个或以上的空行，中间允许包含空格或制表符）
    # \n 后面跟着至少 2 个 ([ \t]*\n)
    pattern = re.compile(r'\n([ \t]*\n){1,}')
    
    # 获取目录下所有 .md 文件（递归）
    folder_path = Path(directory)
    md_files = folder_path.rglob('*.md')
    
    modified_count = 0
    
    print(f"开始扫描目录: {folder_path.resolve()}")
    
    for file_path in md_files:
        try:
            # 以 UTF-8 编码读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 执行正则替换
            new_content = pattern.sub('\n\n', content)
            
            # 如果内容发生变化，则覆盖写入原文件
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"已清理空行: {file_path}")
                modified_count += 1
                
        except Exception as e:
            print(f"读取或写入文件 {file_path} 时出错: {e}")
            
    print(f"\n处理完成！共修改了 {modified_count} 个 .md 文件。")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        TARGET_DIR = sys.argv[1]
    else:
        TARGET_DIR = '.'
    compress_blank_lines(TARGET_DIR)