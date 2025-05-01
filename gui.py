import tkinter as tk
from tkinter import filedialog, simpledialog
import re

# 6. 파일 다이얼로그 GUI (사용자 파일명 입력 기능 추가)
def select_file(title="Select an Image File", filetypes=(("Images", "*.png *.jpg *.jpeg"),)):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def select_directory(title="Select Output Directory"):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title=title)

def get_output_filename(default_name="generated_music.mp3"):
    root = tk.Tk()
    root.withdraw()
    filename = simpledialog.askstring("파일명 입력", "저장할 MP3 파일명을 입력하세요:", initialvalue=default_name)
    
    # 취소 시 기본 이름 사용
    if filename is None:
        return default_name
    
    # 파일 확장자 확인 및 추가
    if not filename.lower().endswith('.mp3'):
        filename += '.mp3'
    
    # 윈도우 금지 문자 제거
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    
    return filename
