from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import glob

# RAG 관련 임포트
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA

# 환경 변수 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 지식 베이스 디렉토리 경로
KNOWLEDGE_BASE_DIR = "knowledge_base"

# 벡터 저장소 초기화 함수
def initialize_vector_store():
    """지식 베이스 문서를 로드하고 벡터 저장소를 초기화합니다."""
    try:
        # 지식 베이스 디렉토리가 존재하는지 확인
        if not os.path.exists(KNOWLEDGE_BASE_DIR):
            os.makedirs(KNOWLEDGE_BASE_DIR)
            print(f"Created directory: {KNOWLEDGE_BASE_DIR}")
        
        # 지식 베이스 파일 로드
        documents = []
        print(f"Looking for files in: {os.path.abspath(KNOWLEDGE_BASE_DIR)}")
        
        file_paths = glob.glob(f"{KNOWLEDGE_BASE_DIR}/*.txt")
        print(f"Found {len(file_paths)} files: {file_paths}")
        
        for file_path in file_paths:
            try:
                print(f"Loading file: {file_path}")
                # 파일 엔코딩 명시적 지정
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
                print(f"Successfully loaded: {file_path}")
            except Exception as e:
                print(f"Error loading file {file_path}: {str(e)}")
                continue
        
        # 문서가 없으면 빈 벡터 저장소 반환
        if not documents:
            print("No documents loaded from knowledge base.")
            return None
        
        print(f"Loaded {len(documents)} documents.")
        
        # 문서 분할
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        print(f"Split into {len(texts)} text chunks.")
        
        # 임베딩 모델 초기화
        embeddings = GoogleGenerativeAIEmbeddings(google_api_key=GOOGLE_API_KEY, model="models/embedding-001")
        
        # 벡터 저장소 생성
        vector_store = FAISS.from_documents(texts, embeddings)
        print("Vector store created successfully.")
        
        return vector_store
    except Exception as e:
        print(f"Error in initialize_vector_store: {str(e)}")
        # 오류 발생 시 빈 벡터 저장소 반환
        return None

# 커스텀 프롬프트 템플릿 정의
template = """당신은 AURA, 이미지，영상과 오디오를 분석할 수 있는 AI 어시스턴트입니다.
당신은 이미지나 영상을 업로드하면 음악을 생성해 드리고, 음악을 업로드하면 이미지를 생성해 드립니다.

사용자가 사용하는 언어에 따라 한국어, 중국어 또는 영어로 답변합니다. 중국어로 질문하면 중국어로, 한국어로 질문하면 한국어로 답변합니다. 각 언어에 맞게 인사말의 변형을 만들어 사용하세요.

현재 대화 기록:
{history}

인간: {input}
AI: """

PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template=template
)

def get_chatbot():
    """
    Google Gemini 모델과 함께 LangChain 대화 체인 초기화 및 반환
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다")
    
    # Gemini 모델 초기화
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7,
        top_p=0.9,
        convert_system_message_to_human=True
    )
    
    # 대화 메모리 초기화
    memory = ConversationBufferMemory(return_messages=True)
    
    # 대화 체인 생성
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=PROMPT,
        verbose=True
    )
    
    # 벡터 저장소 초기화
    vector_store = initialize_vector_store()
    
    # RAG 체인 생성 (벡터 저장소가 있는 경우)
    if vector_store:
        retriever = vector_store.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            verbose=True
        )
    else:
        qa_chain = None
    
    return conversation, qa_chain

def process_message(conversation, qa_chain=None, message="", image_url=None, video_url=None, audio_url=None):
    """
    사용자 메시지 처리 및 AI 응답 반환
    
    Args:
        conversation: LangChain 대화 체인
        qa_chain: RAG 질의응답 체인 (선택사항)
        message: 사용자 텍스트 메시지
        image_url: 업로드된 이미지 URL (선택사항)
        video_url: 업로드된 영상 URL (선택사항)
        audio_url: 업로드된 오디오 파일 URL (선택사항)
        
    Returns:
        AI 응답 텍스트
    """
    # 미디어 정보와 함께 입력 준비
    input_text = message
    
    if image_url:
        input_text += f"\n[사용자가 이미지를 업로드했습니다: {image_url}]"
    
    if video_url:
        input_text += f"\n[사용자가 영상을 업로드했습니다: {video_url}]"
    
    if audio_url:
        input_text += f"\n[사용자가 오디오 파일을 업로드했습니다: {audio_url}]"
    
    # 인사말 패턴 감지 (간단한 인사말인 경우 RAG 사용)
    greeting_keywords = ['안녕', '你好', 'hello', 'hi', '반가워', '안녕하세요', '嗨', '哈喽']
    
    # 사용자 메시지가 간단한 인사말인지 확인
    is_simple_greeting = any(keyword in message.lower() for keyword in greeting_keywords) and len(message) < 20
    
    if is_simple_greeting and qa_chain:
        # 언어 감지
        detected_language = "korean"  # 기본값
        
        if any(keyword in message for keyword in ['你好', '嗨', '哈喽']):
            detected_language = "chinese"
            query = "关于AURA服务的介绍和功能说明"
        elif any(keyword in message for keyword in ['hello', 'hi']):
            detected_language = "english"
            query = "Introduction and features of AURA service"
        else:
            detected_language = "korean"
            query = "AURA 서비스의 소개와 기능 설명"
        
        try:
            # RAG를 사용하여 지식 베이스에서 정보 검색
            rag_result = qa_chain({"query": query})
            raw_response = rag_result.get('result', '')
            
            # Gemini를 사용하여 검색된 정보를 재구성
            rewrite_prompt = f"""
            다음 정보를 기반으로 사용자에게 매우 간결하고 정확한 응답을 제공해주세요.
            사용자 질문: {message}
            검색된 정보: {raw_response}
            
            중요 지침:
            1. 응답은 반드시 1-2줄 이내로 제한해야 합니다.
            2. 정보의 핵심만 포함하고 불필요한 설명은 제외하세요.
            3. 응답은 자연스럽고 친절해야 합니다.
            4. 중요 키워드나 기능은 '*'로 강조해주세요 (예: *이미지 변환*)
            5. 긴 문장 대신 짧은 문장을 사용하고, 적절한 구분으로 가독성을 높이세요.
            
            응답은 다음 언어로 작성해주세요: {detected_language}
            """
            
            # Gemini를 사용하여 응답 생성
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.2,  # 더 낮은 온도로 일관성 향상
                max_output_tokens=100  # 더 짧은 출력 제한
            )
            final_response = llm.invoke(rewrite_prompt).content
            
            # 후처리: 응답 길이 제한 및 포맷팅
            # 언어별 문장 구분자
            sentence_separators = {
                "korean": [".", "다.", "요.", "!", "?"],
                "chinese": ["\u3002", "!", "?"],  # 。는 중국어 문장 구분자
                "english": [".", "!", "?"]
            }
            
            # 현재 언어에 맞는 구분자 가져오기
            separators = sentence_separators.get(detected_language, [".", "!", "?"])
            
            # 문장 분할
            sentences = []
            current = ""
            for char in final_response:
                current += char
                # 문장 끝이 발견되면 추가
                if any(current.endswith(sep) for sep in separators):
                    sentences.append(current.strip())
                    current = ""
            
            # 마지막 문장이 남아있는 경우 추가
            if current.strip():
                sentences.append(current.strip())
            
            # 문장 수 제한 (2문장으로 제한)
            if len(sentences) > 2:
                sentences = sentences[:2]
            
            # 문장 길이 제한
            for i, sentence in enumerate(sentences):
                if len(sentence) > 50:
                    sentences[i] = sentence[:47] + "..."
            
            # 최종 응답 재구성
            final_response = " ".join(sentences)
            
            return final_response            
        except Exception as e:      
            print(f"RAG 오류 발생: {str(e)}")
            # 언어에 따른 기본 인사말 사용
            if detected_language == "chinese":
                return "你好！我是AURA，可以将图像和视频转换为音乐，将音乐转换为图像。请上传图像、视频， 或音乐，我将为您提供转换服务。有什么可以帮到您的吗？"
            elif detected_language == "english":
                return "Hello! I'm AURA, an AI that converts images or videos to music and music to images. How can I help you today?"
            else:
                return "안녕하세요! AURA입니다. 이미지나 영상을 업로드하면 음악을 생성해 드리고, 음악을 업로드하면 이미지를 생성해 드립니다. 무엇을 도와드릴까요?"
    
    # 간단한 인사말이 아니거나 RAG가 없는 경우 모델로부터 응답 받기
    response = conversation.predict(input=input_text)
    return response
