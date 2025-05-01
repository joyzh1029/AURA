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
            base_dir = os.path.dirname(__file__)
            key_path = os.path.join(base_dir, "..", "keys", "gemini_api_key.txt")
            if not os.path.exists(key_path):
                raise FileNotFoundError("Gemini API 키 파일을 찾을 수 없습니다: keys/gemini_api_key.txt")

            with open(key_path, "r") as f:
                self.api_key = f.read().strip()

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

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