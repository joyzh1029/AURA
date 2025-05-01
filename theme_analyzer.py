import random
import hashlib
from setup import nlp
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# SentenceTransformer 기반 의미 유사도 계산을 위해 라이브러리 임포트 (pip install sentence-transformers)
from sentence_transformers import SentenceTransformer, util

# SentenceTransformer 모델 초기화 (한 번만 로드)
sent_transformer = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def rank_candidates(caption, candidates):
    """
    주어진 캡션과 후보 항목들의 의미적 유사도를 계산해
    가장 유사도가 높은 후보를 반환하는 함수.
    """
    caption_embedding = sent_transformer.encode(caption, convert_to_tensor=True)
    candidate_embeddings = sent_transformer.encode(candidates, convert_to_tensor=True)
    similarities = util.cos_sim(caption_embedding, candidate_embeddings)[0]
    best_idx = similarities.argmax().item()
    return candidates[best_idx]

# 지능형 주제 분석 시스템
class IntelligentThemeAnalyzer:
    def __init__(self):
        # 장면 유형에 따른 음악 장르 매핑 테이블
        self.scene_to_genre_map = {
            # 자연/풍경 관련
            "nature": ["ambient", "folk", "classical", "cinematic", "lofi"],
            "landscape": ["ambient", "folk", "classical", "orchestral", "cinematic"],
            "mountain": ["folk", "orchestral", "ambient", "cinematic"],
            "sea": ["ambient", "classical", "electronic", "lofi", "orchestral"],
            "beach": ["reggae", "pop", "lofi", "chill", "acoustic"],
            "forest": ["folk", "ambient", "acoustic", "orchestral"],
            "sunset": ["ambient", "lofi", "jazz", "chill", "synthwave"],
            "sunrise": ["orchestral", "ambient", "classical", "electronic"],
            "sky": ["ambient", "electronic", "orchestral", "synthwave"],
            "snow": ["classical", "ambient", "cinematic", "lofi"],
            "desert": ["folk", "ambient", "world", "cinematic"],
            
            # 도시/인공물 관련
            "city": ["electronic", "jazz", "synthwave", "hip hop", "lofi"],
            "street": ["hip hop", "jazz", "lofi", "electronic", "funk"],
            "building": ["electronic", "jazz", "ambient", "synthwave"],
            "architecture": ["classical", "electronic", "jazz", "ambient"],
            "car": ["rock", "electronic", "synthwave", "hip hop"],
            "technology": ["electronic", "techno", "synthwave", "experimental"],
            "computer": ["electronic", "techno", "synthwave", "glitch"],
            
            # 사람/인물 관련
            "person": ["pop", "indie", "acoustic", "R&B", "soul"],
            "people": ["pop", "folk", "indie", "electronic", "orchestral"],
            "crowd": ["electronic", "rock", "orchestral", "pop"],
            "family": ["pop", "folk", "acoustic", "jazz", "orchestral"],
            "child": ["pop", "folk", "acoustic", "playful", "orchestral"],
            "children": ["playful", "pop", "folk", "orchestral"],
            "woman": ["pop", "R&B", "soul", "indie", "jazz"],
            "man": ["rock", "pop", "indie", "R&B", "blues"],
            "elderly": ["jazz", "classical", "folk", "blues"],
            
            # 행동/활동 관련
            "running": ["electronic", "rock", "drum and bass", "techno", "dubstep"],
            "dancing": ["pop", "electronic", "funk", "disco", "house"],
            "swimming": ["electronic", "ambient", "pop", "lofi", "chill"],
            "jumping": ["electronic", "rock", "pop", "dubstep"],
            "eating": ["jazz", "lofi", "bossa nova", "acoustic"],
            "reading": ["classical", "jazz", "lofi", "ambient", "acoustic"],
            "sleeping": ["ambient", "lofi", "classical", "chill"],
            "walking": ["indie", "folk", "pop", "lofi", "acoustic"],
            
            # 감정/분위기 관련
            "happy": ["pop", "funk", "electronic", "reggae", "jazz"],
            "sad": ["piano", "classical", "indie", "ambient", "blues"],
            "angry": ["rock", "metal", "industrial", "dubstep", "drum and bass"],
            "peaceful": ["ambient", "classical", "lofi", "chill", "new age"],
            "excited": ["rock", "electronic", "pop", "drum and bass", "house"],
            "romantic": ["R&B", "soul", "jazz", "classical", "pop ballad"],
            "mysterious": ["ambient", "electronic", "experimental", "cinematic", "dark jazz"],
            "scary": ["dark ambient", "industrial", "cinematic", "experimental", "dark electronic"],
            
            # 특수 상황/장소 관련
            "party": ["house", "pop", "electronic", "funk", "disco"],
            "wedding": ["classical", "pop", "jazz", "orchestral", "acoustic"],
            "funeral": ["classical", "ambient", "piano", "orchestral"],
            "concert": ["rock", "electronic", "pop", "orchestral"],
            "museum": ["classical", "ambient", "jazz", "electronic", "experimental"],
            "restaurant": ["jazz", "bossa nova", "lofi", "acoustic"],
            "office": ["lofi", "ambient", "jazz", "electronic"],
            "school": ["indie", "pop", "lofi", "acoustic", "orchestral"],
            "hospital": ["ambient", "piano", "orchestral", "electronic"],
            "church": ["classical", "orchestral", "choir", "ambient", "organ"],
            
            # 날씨/시간 관련
            "rain": ["ambient", "jazz", "lofi", "piano", "acoustic"],
            "storm": ["orchestral", "cinematic", "electronic", "rock", "industrial"],
            "cloudy": ["indie", "ambient", "lofi", "jazz", "electronic"],
            "sunny": ["pop", "reggae", "funk", "indie", "electronic"],
            "night": ["electronic", "jazz", "ambient", "synthwave", "trip hop"],
            "day": ["pop", "indie", "folk", "funk", "acoustic"],
            "dawn": ["ambient", "classical", "piano", "orchestral", "chill"],
            "dusk": ["ambient", "jazz", "lofi", "synthwave", "chillwave"],
            
            # 동물 관련
            "animal": ["folk", "orchestral", "ambient", "playful", "acoustic"],
            "dog": ["playful", "folk", "pop", "acoustic"],
            "cat": ["jazz", "lofi", "ambient", "electronic", "playful"],
            "bird": ["classical", "ambient", "folk", "orchestral", "new age"],
            "fish": ["ambient", "electronic", "lofi", "new age"],
            "horse": ["folk", "country", "orchestral", "acoustic"],
            
            # 음식 관련
            "food": ["jazz", "lofi", "bossa nova", "acoustic", "funk"],
            "drink": ["lofi", "jazz", "electronic", "chill", "funk"],
            "restaurant": ["jazz", "bossa nova", "lofi", "acoustic", "easy listening"],
            
            # 예술/엔터테인먼트 관련
            "art": ["experimental", "jazz", "classical", "electronic", "ambient"],
            "music": ["jazz", "classical", "electronic", "ambient", "fusion"],
            "painting": ["classical", "jazz", "ambient", "impressionist", "electronic"],
            "sculpture": ["classical", "ambient", "electronic", "experimental"],
            "book": ["classical", "jazz", "ambient", "lofi", "acoustic"],
            "movie": ["orchestral", "cinematic", "electronic", "jazz", "synthwave"],
            "dance": ["electronic", "pop", "funk", "world", "house"],
            "theater": ["classical", "jazz", "orchestral", "cinematic"],
            
            # 직업/역할 관련
            "soldier": ["orchestral", "cinematic", "rock", "martial", "epic"],
            "police": ["rock", "cinematic", "electronic", "funk", "orchestral"],
            "doctor": ["ambient", "jazz", "electronic", "orchestral"],
            "teacher": ["indie", "acoustic", "orchestral", "jazz", "classical"],
            "student": ["indie", "pop", "lofi", "electronic", "rock"],
            "worker": ["rock", "industrial", "electronic", "folk", "country"],
            "athlete": ["electronic", "rock", "orchestral", "hip hop", "cinematic"],
            "artist": ["jazz", "experimental", "indie", "electronic", "ambient"],
            "musician": ["jazz", "classical", "rock", "electronic", "fusion"],
            
            # 스포츠/활동 관련
            "sport": ["electronic", "rock", "orchestral", "cinematic", "hip hop"],
            "football": ["rock", "electronic", "orchestral", "hip hop"],
            "basketball": ["hip hop", "electronic", "funk", "rock"],
            "baseball": ["rock", "orchestral", "folk", "cinematic"],
            "soccer": ["electronic", "orchestral", "rock", "world", "cinematic"],
            "tennis": ["electronic", "orchestral", "pop", "funk"],
            "swimming": ["ambient", "electronic", "orchestral", "chill"],
            "running": ["electronic", "rock", "drum and bass", "techno"],
            
            # 기타 주제
            "space": ["ambient", "electronic", "cinematic", "orchestral", "synthwave"],
            "galaxy": ["ambient", "electronic", "cinematic", "orchestral", "synthwave"],
            "universe": ["ambient", "electronic", "orchestral", "cinematic", "new age"],
            "robot": ["electronic", "techno", "industrial", "synthwave", "glitch"],
            "alien": ["electronic", "ambient", "experimental", "cinematic"],
            "fantasy": ["orchestral", "celtic", "cinematic", "new age", "folk"],
            "magic": ["orchestral", "cinematic", "electronic", "new age", "celtic"],
            "war": ["orchestral", "cinematic", "rock", "metal", "martial"],
            "battle": ["orchestral", "cinematic", "rock", "metal", "martial"],
            "medieval": ["folk", "celtic", "orchestral", "cinematic", "acoustic"],
            "future": ["electronic", "synthwave", "techno", "ambient", "cinematic"],
            "ancient": ["world", "orchestral", "ambient", "folk", "cinematic"],
            "history": ["orchestral", "classical", "folk", "cinematic", "world"],
        }
        
        # 감정/분위기 키워드에 따른 스타일 매핑 테이블
        self.emotion_to_style_map = {
            # 긍정적 감정
            "happy": ["upbeat and energetic", "bright and cheerful", "groovy and rhythmic"],
            "joy": ["bright and cheerful", "upbeat and energetic", "hopeful and inspiring"],
            "cheerful": ["bright and cheerful", "upbeat and energetic", "groovy and rhythmic"],
            "playful": ["upbeat and energetic", "bright and cheerful", "groovy and rhythmic"],
            "exciting": ["upbeat and energetic", "dramatic and powerful", "chaotic and complex"],
            "peaceful": ["relaxing and mellow", "dreamy and ethereal", "subtle and minimalist"],
            "calm": ["relaxing and mellow", "dreamy and ethereal", "smooth and flowing"],
            "relaxed": ["relaxing and mellow", "dreamy and ethereal", "smooth and flowing"],
            "romantic": ["intimate and emotional", "dreamy and ethereal", "smooth and flowing"],
            "hopeful": ["hopeful and inspiring", "bright and cheerful", "epic and grand"],
            "energetic": ["upbeat and energetic", "groovy and rhythmic", "chaotic and complex"],
            
            # 부정적 감정
            "sad": ["melancholic and sad", "intimate and emotional", "subtle and minimalist"],
            "melancholic": ["melancholic and sad", "intimate and emotional", "dreamy and ethereal"],
            "gloomy": ["melancholic and sad", "dark and intense", "mysterious and intriguing"],
            "angry": ["aggressive and heavy", "dark and intense", "chaotic and complex"],
            "tense": ["dark and intense", "mysterious and intriguing", "chaotic and complex"],
            "anxious": ["chaotic and complex", "dark and intense", "mysterious and intriguing"],
            "fearful": ["dark and intense", "mysterious and intriguing", "chaotic and complex"],
            "mysterious": ["mysterious and intriguing", "dark and intense", "dreamy and ethereal"],
            "lonely": ["melancholic and sad", "intimate and emotional", "subtle and minimalist"],
            
            # 중립적/기타 감정
            "nostalgic": ["retro and nostalgic", "intimate and emotional", "dreamy and ethereal"],
            "epic": ["epic and grand", "dramatic and powerful", "hopeful and inspiring"],
            "dramatic": ["dramatic and powerful", "epic and grand", "dark and intense"],
            "futuristic": ["futuristic and experimental", "electronic and synthetic", "mysterious and intriguing"],
            "ethereal": ["dreamy and ethereal", "subtle and minimalist", "mysterious and intriguing"],
            "intense": ["dark and intense", "aggressive and heavy", "dramatic and powerful"],
            "serene": ["relaxing and mellow", "dreamy and ethereal", "subtle and minimalist"],
            "chaotic": ["chaotic and complex", "aggressive and heavy", "dark and intense"],
            "whimsical": ["dreamy and ethereal", "bright and cheerful", "playful and light"],
            "powerful": ["dramatic and powerful", "epic and grand", "aggressive and heavy"],
            "gentle": ["relaxing and mellow", "intimate and emotional", "subtle and minimalist"],
        }
        
        # 악기 매핑 테이블
        self.genre_to_instrument_map = {
            "rock": ["featuring strong guitar riffs", "with powerful drums", "with deep bass lines"],
            "pop": ["with melodic synthesizers", "with catchy vocal hooks", "with electronic beats"],
            "electronic": ["with electronic synths", "with deep bass lines", "with digital effects"],
            "classical": ["with orchestral strings", "with melodic piano", "with intricate arrangements"],
            "jazz": ["with smooth saxophone", "with jazz piano", "with upright bass"],
            "hip hop": ["with deep bass lines", "with rhythmic percussion", "with vocal samples"],
            "R&B": ["with smooth vocal harmonies", "with soulful melodies", "with rhythmic beats"],
            "ambient": ["with ethereal pads", "with ambient textures", "with atmospheric sounds"],
            "folk": ["with acoustic guitar", "with folk instruments", "with warm vocals"],
            "indie": ["with indie guitar sounds", "with natural drums", "with vocal harmonies"],
            "metal": ["with heavy guitar distortion", "with double bass drums", "with powerful vocals"],
            "blues": ["with bluesy guitar", "with soulful vocals", "with blues piano"],
            "country": ["with country fiddle", "with steel guitar", "with acoustic elements"],
            "funk": ["with funky bass lines", "with rhythm guitar", "with brass sections"],
            "soul": ["with soulful vocals", "with warm organ sounds", "with brass sections"],
            "reggae": ["with reggae rhythm guitar", "with deep bass lines", "with island percussion"],
            "techno": ["with electronic beats", "with synthesizer leads", "with digital effects"],
            "house": ["with house beats", "with electronic synths", "with vocal samples"],
            "dubstep": ["with wobble bass", "with heavy drops", "with electronic beats"],
            "orchestral": ["with full orchestra", "with string sections", "with brass sections"],
            "cinematic": ["with cinematic drums", "with orchestral arrangements", "with dramatic dynamics"],
            "lofi": ["with lo-fi beats", "with vinyl crackle", "with mellow piano"],
            "synthwave": ["with retro synthesizers", "with 80s drum machines", "with nostalgic melodies"],
            "trip hop": ["with downtempo beats", "with atmospheric samples", "with deep bass"],
            "drum and bass": ["with fast breakbeats", "with deep sub bass", "with electronic elements"],
        }
        
        # NLP 도구 초기화
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def analyze_caption(self, caption):
        """이미지 설명을 분석하여 적절한 음악 장르, 스타일, 악기를 선택"""
        # 텍스트 전처리
        doc = nlp(caption.lower())
        keywords = []
        entities = []
        emotions = []
        
        # spaCy 엔티티 및 명사구 추출
        for entity in doc.ents:
            entities.append(entity.text.lower())
        for chunk in doc.noun_chunks:
            entities.append(chunk.text.lower())
        
        # 중요 단어 추출 (불용어, 문장부호 제거 및 품사 태깅)
        for token in doc:
            if token.text.lower() not in self.stop_words and not token.is_punct and len(token.text) > 2:
                if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'PROPN']:
                    lemma = self.lemmatizer.lemmatize(token.text.lower())
                    keywords.append(lemma)
                    if token.pos_ == 'ADJ' and lemma in self.emotion_to_style_map:
                        emotions.append(lemma)
        
        # 키워드를 이용하여 장르 매핑 (장르 점수 부여)
        genre_scores = {}
        for keyword in keywords + entities:
            for word in keyword.split():
                lemma = self.lemmatizer.lemmatize(word)
                if lemma in self.scene_to_genre_map:
                    for genre in self.scene_to_genre_map[lemma]:
                        if genre in genre_scores:
                            genre_scores[genre] += 1
                        else:
                            genre_scores[genre] = 1
        
        # 장르 선택: 후보가 없으면 기본 장르, 있으면 최고 점수 후보 중 AI 랭킹을 사용하여 결정
        if not genre_scores:
            default_genres = ["orchestral", "electronic", "ambient", "cinematic", "pop"]
            selected_genre = rank_candidates(caption, default_genres)
        else:
            max_score = max(genre_scores.values())
            top_genres = [genre for genre, score in genre_scores.items() if score == max_score]
            selected_genre = rank_candidates(caption, top_genres) if len(top_genres) > 1 else top_genres[0]
        
        # 악기 선택: 선택된 장르에 따라 후보 리스트에서 AI 랭킹을 통해 결정
        if selected_genre in self.genre_to_instrument_map:
            instrument_options = self.genre_to_instrument_map[selected_genre]
            selected_instrument = rank_candidates(caption, instrument_options)
        else:
            default_instruments = [
                "with melodic elements", 
                "with rhythmic percussion", 
                "with electronic sounds",
                "with acoustic elements"
            ]
            selected_instrument = rank_candidates(caption, default_instruments)
        
        # 감정 검출: 키워드 중 emotion_to_style_map에 포함된 단어 선택
        detected_emotions = []
        for keyword in keywords:
            if keyword in self.emotion_to_style_map:
                detected_emotions.append(keyword)
        
        # 감정이 검출되지 않으면 기본 감정 선택 (장르 기반 선택 포함)
        if not detected_emotions:
            default_emotions = ["peaceful", "energetic", "nostalgic", "mysterious", "dramatic"]
            if selected_genre in ["rock", "metal", "dubstep"]:
                genre_emotions = ["energetic", "powerful", "intense"]
            elif selected_genre in ["ambient", "classical", "lofi"]:
                genre_emotions = ["peaceful", "melancholic", "serene"]
            elif selected_genre in ["pop", "funk", "disco"]:
                genre_emotions = ["cheerful", "energetic", "playful"]
            else:
                genre_emotions = default_emotions
            detected_emotions = [rank_candidates(caption, genre_emotions)]
        
        # 스타일 선택: 각 감정에 해당하는 스타일 후보들을 AI 랭킹으로 선택
        emotion_based_styles = []
        for emotion in detected_emotions[:2]:
            if emotion in self.emotion_to_style_map:
                candidate_styles = self.emotion_to_style_map[emotion]
                best_style = rank_candidates(caption, candidate_styles)
                emotion_based_styles.append(best_style)
        if not emotion_based_styles:
            default_styles = ["upbeat and energetic", "relaxing and mellow", "dramatic and powerful", "mysterious and intriguing"]
            selected_style = rank_candidates(caption, default_styles)
        else:
            # 중복 제거 후 랭킹으로 결정
            selected_style = rank_candidates(caption, list(set(emotion_based_styles)))
        
        return {
            "genre": selected_genre,
            "style": selected_style,
            "instrument": selected_instrument,
            "detected_emotions": detected_emotions[:3]  # 최대 3개 감정 반환
        }

# 음악 프롬프트 생성 (지능형 매핑 사용)
def generate_music_prompt(description):
    analyzer = IntelligentThemeAnalyzer()
    analysis_result = analyzer.analyze_caption(description)
    
    genre = analysis_result["genre"]
    style = analysis_result["style"]
    instrument = analysis_result["instrument"]
    emotions = analysis_result["detected_emotions"]

    emotion_phrase = " and ".join(emotions) if emotions else "neutral"

    # 더욱 정교한 프롬프트 생성
    prompt = (
        f"Create a {genre} music track that is {style}, {instrument}, conveying a {emotion_phrase} mood. "
        f"Use a structured arrangement starting with a soft intro and gradually building up to a climax. "
        f"Incorporate rich harmonies and dynamic changes to enhance the listening experience."
    )

    return prompt, analysis_result

