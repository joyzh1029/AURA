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

def get_query_type(text: str) -> str:
    """메시지 유형 확인"""
    text_lower = text.strip().lower()
    
    # 인사말 패턴
    greetings = {
        "en": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"],
        "zh": ["你好", "您好", "嗨", "早上好", "下午好", "晚上好"],
        "ko": ["안녕", "안녕하세요", "좋은아침", "좋은오후", "좋은저녁"]
    }
    
    # 변환 요청 패턴
    conversion_patterns = {
        "en": ["convert", "change", "transform", "upload"],
        "zh": ["转换", "变成", "生成", "上传"],
        "ko": ["변환", "바꾸", "만들", "업로드"]
    }
    
    # 새로운 변환 요청 키워드
    new_conversion_words = {
        "ko": ["업로드하시면", "파일을", "이미지나", "비디오를"],
        "en": ["upload your", "file to", "image or", "video to"],
        "zh": ["上传您的", "文件来", "图片或", "视频来"]
    }
    
    # 인사말만 있는 경우
    if any(greeting in text_lower for greetings_list in greetings.values() for greeting in greetings_list) and \
       not any(pattern in text_lower for patterns_list in conversion_patterns.values() for pattern in patterns_list):
        return "greeting"
    
    # 변환 요청 확인 - 새로운 조건 추가
    is_conversion = False
    
    # 기본 변환 패턴 확인
    if any(pattern in text_lower for patterns_list in conversion_patterns.values() for pattern in patterns_list):
        is_conversion = True
    
    # 새로운 변환 키워드 확인
    if any(word in text_lower for words_list in new_conversion_words.values() for word in words_list):
        is_conversion = True
    
    # 음악 관련 키워드가 있고 파일 업로드나 변환에 관한 내용이 있는 경우에만 변환으로 처리
    if ("음악" in text_lower or "music" in text_lower or "音乐" in text_lower) and is_conversion:
        return "conversion"
    
    return "other"

def detect_language(text: str) -> str:
    """언어 감지 (한국어, 영어, 중국어 지원)"""
    try:
        # 중국어 키워드 검색
        chinese_keywords = [
            "中文", "回答", "请", "想要", "帮助",
            "音乐", "视频", "图片", "转换"
        ]
        if any(keyword in text for keyword in chinese_keywords):
            return "zh"
            
        # 한국어 키워드 검색
        korean_keywords = [
            "안녕", "음악", "비디오", "이미지", "변환",
            "도와", "주세요", "해주세요"
        ]
        if any(keyword in text for keyword in korean_keywords):
            return "ko"
            
        # langdetect로 추가 검사
        detected = detect(text)
        if detected.startswith("zh"):
            return "zh"
        elif detected.startswith("ko"):
            return "ko"
        elif detected.startswith("en"):
            return "en"
            
        return "en"  # 기본값을 영어로 변경
    except Exception as e:
        print(f"[ERROR] Language detection failed: {str(e)}")
        return "en"  # 예외 시 영어 기본값

def get_translation(text: str, target_lang: str) -> str:
    """간단한 번역 함수"""
    translations = {
        "ko": {
            "Image Conversion": "이미지 변환",
            "Video Conversion": "비디오 변환",
            "Drag and drop": "드래그 앤 드롭",
            "click to select": "클릭하여 선택",
            "automatically": "자동으로",
            "generate": "생성",
            "download": "다운로드",
            "play": "재생"
        },
        "zh": {
            "Image Conversion": "图片转换",
            "Video Conversion": "视频转换",
            "Drag and drop": "拖放",
            "click to select": "点击选择",
            "automatically": "自动",
            "generate": "生成",
            "download": "下载",
            "play": "播放"
        }
    }
    
    if target_lang not in translations:
        return text
        
    result = text
    for eng, trans in translations[target_lang].items():
        result = result.replace(eng, trans)
    
    return result

def validate_translation(text: str, target_lang: str) -> str:
    """출력 언어 확인 및 번역"""
    try:
        # 단순 문자열인 경우 바로 반환
        if len(text.strip()) < 10:
            return text
            
        # 언어 감지
        detected = detect(text)
        print(f"[INFO] Detected response language: {detected}, target: {target_lang}")
        
        if detected == target_lang:
            return text
            
        # 번역 필요
        print(f"[INFO] Translation needed from {detected} to {target_lang}")
        translated = get_translation(text, target_lang)
        
        # 번역 결과 확인
        if len(translated.strip()) > 10:
            print(f"[INFO] Translation successful")
            return translated
        else:
            print(f"[WARNING] Translation may have failed, returning original")
            return text
            
    except Exception as e:
        print(f"[ERROR] Translation validation failed: {str(e)}")
        return text

def initialize_vector_store():
    """벡터 저장소 초기화 (최적화된 청크 설정)"""
    try:
        if not os.path.exists(KNOWLEDGE_BASE_DIR):
            os.makedirs(KNOWLEDGE_BASE_DIR)
            print(f"[INFO] Created knowledge base directory: {KNOWLEDGE_BASE_DIR}")
        
        file_paths = glob.glob(f"{KNOWLEDGE_BASE_DIR}/*.txt")
        print(f"[INFO] Found knowledge base files: {file_paths}")
        
        if not file_paths:
            print("[WARNING] No text files found in knowledge base directory")
            return None
        
        documents = []
        for file_path in file_paths:
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                loaded_docs = loader.load()
                documents.extend(loaded_docs)
                print(f"[INFO] Loaded {len(loaded_docs)} documents from {file_path}")
            except Exception as e:
                print(f"[ERROR] Failed to load {file_path}: {str(e)}")
                continue
        
        if not documents:
            print("[WARNING] No valid documents loaded from knowledge base")
            return None
        
        print(f"[INFO] Total documents loaded: {len(documents)}")
        
        # 최적화된 청크 설정
        text_splitter = CharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separator="\n",
            length_function=len
        )
        
        try:
            texts = text_splitter.split_documents(documents)
            print(f"[INFO] Split into {len(texts)} text chunks")
            
            embeddings = GoogleGenerativeAIEmbeddings(
                google_api_key=GOOGLE_API_KEY, 
                model="models/embedding-001"
            )
            
            vector_store = FAISS.from_documents(texts, embeddings)
            print("[INFO] Vector store initialized successfully")
            return vector_store
            
        except Exception as e:
            print(f"[ERROR] Failed to create vector store: {str(e)}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Vector store initialization failed: {str(e)}")
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
1. You MUST respond ONLY in {lang_map.get(detected_lang)}
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
    """채팅 모델 초기화"""
    try:
        print("[INFO] Initializing chatbot...")
        
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set")
        
        # 모델 초기화
        llm = ChatGoogleGenerativeAI(
            google_api_key=GOOGLE_API_KEY,
            model="gemini-1.5-flash",
            temperature=0.7,
            convert_system_message_to_human=True
        )
        print("[INFO] LLM initialized successfully")
        
        # 일반 대화용 체인
        conversation = ConversationChain(
            llm=llm,
            memory=ConversationBufferMemory()
        )
        print("[INFO] Conversation chain initialized")
        
        # 지식 기반 QA 체인
        vector_store = initialize_vector_store()
        if vector_store:
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(),
                return_source_documents=True
            )
            print("[INFO] QA chain initialized with vector store")
        else:
            qa_chain = None
            print("[WARNING] QA chain initialization failed - no vector store")
            
        return conversation, qa_chain
    except Exception as e:
        print(f"[ERROR] Failed to initialize chatbot: {str(e)}")
        # 创建一个基本的对话链作为后备
        basic_llm = ChatGoogleGenerativeAI(
            google_api_key=GOOGLE_API_KEY,
            model="gemini-pro",
            temperature=0.7
        )
        basic_conversation = ConversationChain(
            llm=basic_llm,
            memory=ConversationBufferMemory()
        )
        return basic_conversation, None
    
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
        # 언어 감지
        detected_lang = detect_language(message)
        print(f"[INFO] Detected language: {detected_lang}, Message: {message[:50]}...")
        
        # 쿼리 유형 판단
        query_type = get_query_type(message)
        print(f"[INFO] Query type detected: {query_type}")
        
        # 인사말 처리
        if query_type == "greeting":
            return get_greeting_response(detected_lang)
            
        # 변환 요청 처리
        elif query_type == "conversion":
            print("[INFO] Conversion request detected, providing guidance")
            if not qa_chain:
                print("[ERROR] QA chain not initialized")
                return get_fallback_response(detected_lang)
                
            # 간단한 응답 템플릿
            conversion_guides = {
                "ko": "이미지나 비디오 파일을 업로드하시면 AI가 분석하여 음악을 생성해드립니다. 지원 형식: JPG, PNG, MP4, AVI",
                "en": "Upload your image or video file and our AI will analyze it to generate music. Supported formats: JPG, PNG, MP4, AVI",
                "zh": "上传您的图片或视频文件，AI将分析并生成音乐。支持格式：JPG、PNG、MP4、AVI"
            }
            
            return conversion_guides.get(detected_lang, conversion_guides["en"])
            
        # 기타 일반 질문 처리
        else:
            print("[INFO] General query detected, using conversation chain")
            try:
                # 사용자 언어에 따른 시스템 메시지
                system_messages = {
                    "ko": "당신은 AURA의 AI 어시스턴트입니다. 이미지와 비디오를 음악으로 변환하는 서비스를 제공합니다. 2-3줄로 간단명료하게 답변해주세요.",
                    "en": "You are AURA's AI assistant that converts images and videos to music. Keep your responses brief and clear, within 2-3 lines.",
                    "zh": "你是AURA的AI助手，可以将图片和视频转换为音乐。请用2-3行简短的语言回答问题。"
                }
                
                # 시스템 메시지 설정
                conversation.memory.chat_memory.add_user_message(system_messages.get(detected_lang, system_messages["en"]))
                
                # Gemini로 응답 생성
                response = conversation.predict(input=message)
                print(f"[INFO] Generated response using conversation chain")
                
                # 응답 검증 및 번역
                if response and len(response.strip()) > 0:
                    # 응답을 2-3줄로 제한
                    lines = [line for line in response.strip().split('\n') if line.strip()]
                    short_response = '\n'.join(lines[:3])
                    
                    validated_response = validate_translation(short_response, detected_lang)
                    if len(validated_response.strip()) > 0:
                        return validated_response
                        
                print("[WARNING] Empty or invalid response from conversation chain")
                
            except Exception as e:
                print(f"[ERROR] Conversation chain error: {str(e)}")
                
            return get_fallback_response(detected_lang)
                
    except Exception as e:
        print(f"[ERROR] Message processing failed: {str(e)}")
        return get_fallback_response(detected_lang)


def get_fallback_response(lang: str) -> str:
    """언어별 안전망 응답"""
    fallback_responses = {
        "ko": "죄송합니다. 일시적인 문제가 발생했습니다. 잠시 후에 다시 시도해주세요.",
        "en": "I apologize for the temporary issue. Please try again in a moment.",
        "zh": "对不起，出现了临时问题。请稍后再试。"
    }
    return fallback_responses.get(lang, fallback_responses["en"])

def generate_fallback_response(lang: str) -> str:
    """兼容旧的函数名"""
    return get_fallback_response(lang)

def get_greeting_response(lang: str) -> str:
    """언어별 인사말 응답"""
    greetings = {
        "ko": "안녕하세요! AURA입니다. 이미지나 비디오를 음악으로 변환해드립니다.",
        "en": "Hello! This is AURA. I can convert your images or videos into music.",
        "zh": "您好！这里是AURA。我可以将您的图片或视频转换成音乐。"
    }
    return greetings.get(lang, greetings["en"])

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
