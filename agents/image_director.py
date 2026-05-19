"""
Stage 4: 시네마틱 이미지 프롬프트 생성 에이전트 (image_director.py)

각 챕터에 어울리는 시네마틱 실사 이미지 프롬프트를 생성합니다.
- 실제 이미지 생성은 Antigravity의 generate_image 도구가 수행
- 이 에이전트는 프롬프트 텍스트를 준비하고 매핑 정보를 저장
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 챕터별 이미지 프롬프트 기본 매핑
DEFAULT_IMAGE_PROMPTS = {
    "cover": "A majestic leather-bound antique book floating in cosmic golden light, surrounded by ethereal mist and stars, cinematic photorealistic, 8K, warm tones",
    "preface": "A warm sunlit vintage study room with an open ancient book on a mahogany desk, golden dust particles in light beams, cinematic photorealistic 8K",
    "part1": "A lone ancient oak tree standing tall on a hilltop at golden hour, roots deep in earth, branches reaching toward infinite sky, cinematic 8K photorealistic",
    "part2": "A crystal clear mountain stream flowing through an enchanted forest at sunrise, mist rising from water reflecting golden sky, cinematic photorealistic 8K",
    "part3": "A person silhouetted standing at the peak of a mountain overlooking vast clouds below at golden hour, arms open embracing the horizon, cinematic 8K",
    "commentary": "Ancient scrolls and philosophical texts from East and West arranged on a weathered wooden table, soft candlelight, ink brush nearby, cinematic 8K",
    "commentary_lucky": "A magnificent butterfly emerging from a golden chrysalis in morning sunlight, dewdrops on petals, magical transformation moment, cinematic 8K",
    "commentary_eastwest": "An ancient Eastern temple garden meets a Western classical library in a surreal blend, cherry blossoms and marble columns, golden hour, cinematic 8K",
    "conclusion": "A majestic white swan gliding on a perfectly still lake at sunset, mountains reflected in water, ethereal golden light, cinematic photorealistic 8K",
    "appendix": "A curated collection of beautiful classic books arranged like stepping stones leading toward a brilliant sunrise horizon, cinematic 8K",
}

def run(book, settings, state):
    """Stage 4 메인 실행 함수"""
    book_id = book["id"]
    images_dir = os.path.join(ROOT, "images")
    
    os.makedirs(images_dir, exist_ok=True)
    
    # 이미지 프롬프트 매핑 파일 생성
    mapping = {}
    
    for scene_id, prompt in DEFAULT_IMAGE_PROMPTS.items():
        image_filename = f"scene_{scene_id}.png"
        image_path = os.path.join(images_dir, image_filename)
        
        mapping[scene_id] = {
            "prompt": prompt,
            "filename": image_filename,
            "exists": os.path.exists(image_path)
        }
        
        status = "존재" if os.path.exists(image_path) else "생성 필요"
        print(f"    [{scene_id}] {status} — {image_filename}")
    
    # 매핑 파일 저장
    mapping_path = os.path.join(ROOT, "state", f"{book_id}_images.json")
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    # 생성이 필요한 이미지 수 확인
    needed = sum(1 for v in mapping.values() if not v["exists"])
    
    if needed > 0:
        print(f"\n  [안내] {needed}개 이미지 생성이 필요합니다.")
        print(f"         Antigravity의 generate_image 도구로 생성하세요.")
        print(f"         프롬프트 매핑: state/{book_id}_images.json")
    else:
        print(f"\n  모든 이미지가 이미 존재합니다.")
    
    return True
