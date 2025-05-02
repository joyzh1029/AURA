import os
<<<<<<< HEAD
=======
from dotenv import load_dotenv
>>>>>>> origin/jaehoon
import google.generativeai as genai

class LLMPromptRefiner:
    def __init__(self, api_key=None):
        """
<<<<<<< HEAD
        Gemini API Key를 받아 초기화. 없으면 keys/gemini_api_key.txt 파일에서 읽는다.
        """
        if api_key:
            self.api_key = api_key
        else:
            # 환경 변수 설치 필요
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
=======
        Gemini API Key를 받아 초기화. 없으면 .env 파일의 GOOGLE_API_KEY를 사용한다.
        """
        load_dotenv()

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GOOGLE_API_KEY")

            if not self.api_key:
                raise ValueError("Gemini API 키가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY를 정의하세요.")
>>>>>>> origin/jaehoon

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

<<<<<<< HEAD
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

=======
    def refine_prompt(self, top_caption: str, top_captions: list = None):
        """
        가장 많이 등장한 자막(top_caption)과 보조 자막 리스트(top_captions)를 바탕으로
        음악 생성에 적합한 감성적 프롬프트를 생성한다.
        """
        captions_section = ""
        if top_captions:
            formatted = "\n".join([f"- {cap}" for cap in top_captions if cap != top_caption])
            captions_section = f"\n참고할 보조 장면 자막:\n{formatted}"

        instruction = (
            "당신은 영상 장면에 어울리는 음악을 작곡하는 창의적인 음악 감독입니다.\n"
            "아래 장면 설명과 보조 설명들을 바탕으로, 감정적이고 서사적인 분위기를 해석하고,\n"
            "그에 어울리는 음악의 스타일, 악기 구성, 장르를 상상해보세요.\n"
            "출력은 반드시 하나의 자연스러운 문장으로 작성되어야 하며,\n"
            "감정과 분위기를 구체적으로 표현해야 합니다.\n"
            "출력은 반드시 영어로 작성되어야 합니다.\n"
            "\n[대표 장면 설명]\n"
            f"{top_caption}"
            f"{captions_section}"
            "\n\n예시:\n"
            "입력: 'A woman is reading a book in a quiet library.'\n"
            "출력: 'A soft classical piano melody echoing through a tranquil library filled with golden afternoon light.'"
        )

        response = self.model.generate_content(instruction)
        refined_text = response.text.strip()

        if not refined_text or len(refined_text) < 10:
            raise ValueError("프롬프트 생성 결과가 너무 짧거나 비어있습니다.")

        return refined_text.split("\n")[0].strip()
>>>>>>> origin/jaehoon
