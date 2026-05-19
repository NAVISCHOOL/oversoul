import os

def replace_terms_in_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define replacements
    # 1. Standard "Over-Soul (초혼)" -> "대령(The Over-Soul)"
    content = content.replace("Over-Soul (초혼)", "대령(The Over-Soul)")
    
    # 2. APP_BOX specific "2. 초혼 (The Over-Soul, 1841)" -> "2. 대령 (The Over-Soul, 1841)"
    content = content.replace("2. 초혼 (The Over-Soul, 1841)", "2. 대령 (The Over-Soul, 1841)")
    
    # 3. List specific "(초혼=플로우 상태)" -> "(대령=플로우 상태)"
    content = content.replace("(초혼=플로우 상태)", "(대령=플로우 상태)")
    
    # 4. List specific "(초혼 원리의 실전 적용)" -> "(대령 원리의 실전 적용)"
    content = content.replace("(초혼 원리의 실전 적용)", "(대령 원리의 실전 적용)")
    
    # 5. General "초혼" replacements
    content = content.replace("초혼", "대령(The Over-Soul)")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Successfully updated terms in {file_path}")

if __name__ == "__main__":
    replace_terms_in_file("versions/final_content_v3.md")
    replace_terms_in_file("translated_soul.md")
