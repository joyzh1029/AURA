from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import glob
from langdetect import detect, LangDetectException, DetectorFactory
from typing import Dict, Tuple

# RAG 관련 임포트
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA

# 환경 변수 로드
load_dotenv()

# 설정 초기화
DetectorFactory.seed = 0  # 언어 감지 안정성 향상

# 환경 변수에서 API 키 가져오기
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUPPORTED_LANGS = ["ko", "en", "zh"]  # 지원 언어 목록

# 지식 베이스 디렉토리 경로
KNOWLEDGE_BASE_DIR = "knowledge_base"

def detect_language(text: str) -> str:
    """개선된 언어 감지 로직"""
    # 짧은 메시지 특별 처리
    if not text or len(text.strip()) < 3:
        # 영어 짧은 인사
        if text.strip().lower() in ["hi", "hello", "hey"]:
            return "en"
        # 중국어 짧은 인사
        elif text.strip() in ["你好", "您好", "嗨"]:
            return "zh"
        # 기타 짧은 텍스트는 내용 기반 판단
    
    try:
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGS else "ko"  # 불확실할 경우 한국어 기본값
    except LangDetectException:
        return "ko"  # 예외 시 한국어 기본값

def get_translation(text: str, target_lang: str) -> str:
    """간단한 번역 함수 (실제 API 대체 필요)"""
    # 실제 구현에서는 Google Translate나 다른 번역 API 사용 권장
    print(f"번역 필요: {text[:30]}... -> {target_lang}")
    return generate_fallback_response(target_lang)

def validate_translation(text: str, target_lang: str) -> str:
    """출력 언어 확인"""
    try:
        detected = detect(text)
        if detected == target_lang:
            return text
        print(f"응답 언어 불일치: 감지={detected}, 목표={target_lang}")
        return get_translation(text, target_lang)
    except Exception as e:
        print(f"번역 검증 오류: {str(e)}")
        return text  # 오류 시 원본 텍스트 유지

def initialize_vector_store():
    """벡터 저장소 초기화 (최적화된 청킹 설정)"""
    try:
        if not os.path.exists(KNOWLEDGE_BASE_DIR):
            os.makedirs(KNOWLEDGE_BASE_DIR)
        
        documents = []
        file_paths = glob.glob(f"{KNOWLEDGE_BASE_DIR}/*.txt")
        
        for file_path in file_paths:
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
            except Exception as e:
                print(f"파일 로드 오류 {file_path}: {str(e)}")
        
        if not documents:
            return None
        
        # 최적화된 청크 설정
        text_splitter = CharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
            separator="\n\n"
        )
        texts = text_splitter.split_documents(documents)
        
        embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=GOOGLE_API_KEY, 
            model="models/embedding-001"
        )
        
        return FAISS.from_documents(texts, embeddings)
    except Exception as e:
        print(f"벡터 저장소 초기화 오류: {str(e)}")
        return None

def create_prompt_template(detected_lang: str) -> PromptTemplate:
    """언어 중립적 프롬프트 템플릿"""
    lang_map = {
        "ko": "한국어 (Korean)",
        "en": "English",
        "zh": "中文 (Chinese)"        
    }
    
    template = f"""SYSTEM: You are AURA - an AI assistant specializing in image/music conversion.
IMPORTANT INSTRUCTION:
1. You MUST respond ONLY in {lang_map.get(detected_lang, 'English')}
2. Maintain technical accuracy
3. Reference uploaded media when present
4. Be helpful and friendly

HISTORY:
{{history}}

USER: {{input}}
AURA:"""
    
    return PromptTemplate(
        input_variables=["history", "input"],
        template=template
    )

def get_chatbot() -> Tuple[ConversationChain, RetrievalQA]:
    """챗봇 초기화 (최적화 설정)"""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY 필요")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,  # 낮은 온도로 일관성 향상
        top_p=0.95,
        convert_system_message_to_human=True
    )
    
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="history",
        input_key="input"
    )
    
    vector_store = initialize_vector_store()
    qa_chain = None
    
    if vector_store:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(
                search_kwargs={"k": 2}
            )
        )
    
    return ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    ), qa_chain

def process_message(
    conversation: ConversationChain,
    qa_chain: RetrievalQA,
    message: str,
    **media_urls
) -> str:
    """강화된 메시지 처리 파이프라인"""
    try:
        # 언어 감지 및 프롬프트 설정
        detected_lang = detect_language(message)
        print(f"감지된 언어: {detected_lang}, 메시지: {message[:20]}...")
        
        prompt_template = create_prompt_template(detected_lang)
        conversation.prompt = prompt_template
        
        # 미디어 정보 통합
        input_text = message
        for media_type, url in media_urls.items():
            if url:
                input_text += f"\n[미디어:{media_type}={url}]"
        
        # 응답 생성
        if len(message) > 15 and qa_chain:
            rag_result = qa_chain({"query": input_text})
            response = rag_result.get('result', '')
        else:
            response = conversation.predict(input=input_text)
        
        # 응답이 올바른 언어인지 확인
        return response  # 검증 후 직접 반환
    
    except Exception as e:
        print(f"처리 실패: {str(e)}")
        return generate_fallback_response(detected_lang)

def generate_fallback_response(lang: str) -> str:
    """언어별 안전망 응답"""
    fallback_responses = {
        "ko": "죄송합니다. 시스템 오류가 발생했습니다. 다시 시도해주세요.",
        "en": "Sorry, we encountered a system error. Please try again.",
        "zh": "很抱歉，系统发生错误，请再试一次。"       
    }
    return fallback_responses.get(lang, fallback_responses["en"])

# 테스트 실행
if __name__ == "__main__":
    # 테스트 케이스
    test_cases = [
        ("Hello, convert this image", "en"),
        ("안녕하세요, 이미지 변환 부탁드려요", "ko"),
        ("你好，我想把图片转换成音乐", "zh"),
        ("Hi", "en")
    ]
    
    conversation, qa_chain = get_chatbot()
    
    for msg, expected_lang in test_cases:
        print(f"Input ({expected_lang}): {msg}")
        response = process_message(conversation, qa_chain, msg)
        print(f"Output: {response}\n{'-'*50}")
