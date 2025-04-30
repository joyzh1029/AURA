import os
import google.generativeai as genai

class LLMPromptRefiner:
    def __init__(self, api_key=None):
        """
        Gemini API Key를 받아 초기화. 없으면 keys/gemini_api_key.txt 파일에서 읽는다.
        """
        if api_key:
            self.api_key = api_key
        else:
            # keys 폴더 안에 gemini_api_key.txt 파일 읽기
            base_dir = os.path.dirname(__file__)
            key_path = os.path.join(base_dir, "..", "keys", "gemini_api_key.txt")
            if not os.path.exists(key_path):
                raise FileNotFoundError("Gemini API 키 파일을 찾을 수 없습니다: keys/gemini_api_key.txt")

            with open(key_path, "r") as f:
                self.api_key = f.read().strip()

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

    def refine_prompt(self, raw_caption):
        """
        BLIP이 만든 원시 문장을 받아, MusicGen용 풍부한 감성 기반 자연어 프롬프트로 변환한다.
        """
        system_instruction = (
            f"당신은 음악을 만드는 인공지능 어시스턴트입니다.\n"
            f"주어진 장면 설명을 기반으로, 장면이 전달하는 전반적인 감성(분위기, 감정, 상황, 시간대, 배경)을 자연스럽게 파악하세요.\n"
            f"단순한 사실 나열이 아니라, 숨겨진 분위기와 스토리까지 해석해야 합니다.\n"
            f"그 감성을 반영하여 음악 스타일, 장르, 분위기를 모두 포함한 자연스러운 하나의 문장으로 프롬프트를 작성하세요.\n"
            f"리스트 형태나 여러 문장을 나열하지 말고, 반드시 하나의 구체적인 자연어 문장으로 작성해야 합니다.\n"
            f"상황에 맞는 감성을 자유롭게 해석하여 반영하세요.\n"
            f"장면 설명: '{raw_caption}'"
        )

        response = self.model.generate_content(system_instruction)
        refined_text = response.text.strip()

        # 만약 여러 줄로 답했을 경우 첫 번째 문장만 사용
        first_line = refined_text.split("\n")[0].strip()

        return first_line

