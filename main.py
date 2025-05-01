import os
from image_captioning import generate_caption
from theme_analyzer import generate_music_prompt
from music_generation import generate_music
from gui import select_file, select_directory, get_output_filename

# 7. 전체 실행 함수 (개선된 버전)
def generate_music_from_image(image_path, output_dir=".", output_filename="generated_music.mp3"):
    # 이미지 설명 추출
    description = generate_caption(image_path)
    
    # 지능형 프롬프트 생성
    prompt, analysis = generate_music_prompt(description)

    print(f"이미지 설명: {description}")
    print(f"감지된 감정/분위기: {', '.join(analysis['detected_emotions'])}")
    print(f"선택된 장르: {analysis['genre']}")
    print(f"선택된 스타일: {analysis['style']}")
    print(f"선택된 악기: {analysis['instrument']}")
    print(f"생성된 프롬프트: {prompt}")

    # 음악 생성 및 저장
    output_path = os.path.join(output_dir, output_filename)
    generate_music(prompt, output_path=output_path)
    
    return description, analysis, prompt, output_path

# 8. 실행
if __name__ == "__main__":
    # 이미지 파일 선택
    image_path = select_file(title="이미지 파일을 선택하세요")
    if not image_path:
        print("이미지 파일이 선택되지 않았습니다.")
    else:
        # 출력 디렉토리 선택
        output_dir = select_directory(title="출력 디렉토리를 선택하세요")
        if not output_dir:
            print("출력 디렉토리가 선택되지 않았습니다.")
        else:
            # 파일명 입력 받기
            output_filename = get_output_filename()
            
            # 음악 생성 실행
            description, analysis, prompt, output_path = generate_music_from_image(
                image_path, 
                output_dir=output_dir,
                output_filename=output_filename
            )
            
            # 결과 출력
            print("\n=== 생성 완료 ===")
            print(f"이미지: {os.path.basename(image_path)}")
            print(f"설명: {description}")
            print(f"감정/분위기: {', '.join(analysis['detected_emotions'])}")
            print(f"장르: {analysis['genre']}")
            print(f"스타일: {analysis['style']}")
            print(f"악기: {analysis['instrument']}")
            print(f"저장된 음악: {output_path}")
