import os
import re
from datetime import datetime

def update_copyright(directory):
    current_year = "2026"
    # Patterns to match:
    # 1. (©|Copyright|(c)) 2020-2024 -> (©|Copyright|(c)) 2020-2026
    # 2. (©|Copyright|(c)) 2024 -> (©|Copyright|(c)) 2024-2026
    
    range_pattern = re.compile(r'((?:©|Copyright|\(c\))\s+[0-9]{4}-)202[0-5]', re.IGNORECASE)
    single_pattern = re.compile(r'((?:©|Copyright|\(c\))\s+)(202[0-5])(?![0-9-])', re.IGNORECASE)

    for root, dirs, files in os.walk(directory):
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            if file.endswith(('.txt', '.md', '.py', '.js', '.ts', '.tsx', '.html', '.css', '.json')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = range_pattern.sub(rf'\1{current_year}', content)
                    new_content = single_pattern.sub(rf'\1\2-{current_year}', new_content)
                    
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    update_copyright(".trae/skills")
    update_copyright("anthropics_skills")
