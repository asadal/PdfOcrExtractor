import os
import PyPDF3
import streamlit as st
import tempfile as tf
from tempfile import NamedTemporaryFile
import pytesseract
from tqdm import tqdm
from pdf2image import convert_from_path
import cv2
import re

def extract_text_from_img(img):
    # pytesseract.pytesseract.tesseract_cmd = '/tesseract-ocr/tessdata/'
    config = ('-l kor+eng')
    text_string = pytesseract.image_to_string(img).strip()
    # text_string = pytesseract.image_to_string(img, config=config).strip()
    return text_string

def output_text(st, final_txt):
    st.header("추출된 텍스트")
    st.text_area("", value=final_txt, height=500)
    st.header("텍스트 다운로드")
    st.download_button(
        label="📥 Download ⏱",
        data=final_txt,
        file_name='extracted_text.txt',
        mime='text/plain'
    )

def process_line_breaks(file_path):
    try:
        # 파일을 읽기 모드로 열기
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 두 번 이상의 줄바꿈을 임시 문자로 변경
        content = re.sub(r'\n{2,}', 'TEMP_NEWLINE', content)
        # 남은 단일 줄바꿈을 공백으로 변경
        modified_content = content.replace('\n', ' ')
        # 임시 문자를 원래 줄바꿈으로 변경
        modified_content = modified_content.replace('TEMP_NEWLINE', '\n\n')
        
        # 수정된 내용을 새로운 파일에 저장
        new_file_path = file_path.replace('.txt', '_final.txt')
        with open(new_file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(modified_content)
        print(f'수정된 파일이 저장되었습니다: {new_file_path}')
        return new_file_path
    except Exception as e:
        print(f'오류 발생: {e}')

def app():
    st.set_page_config(page_title="PDF Extractor", page_icon="https://cdn-icons-png.flaticon.com/512/29/29099.png")
    st.image("https://cdn-icons-png.flaticon.com/512/29/29099.png", width=120)
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("텍스트 추출기")
    with col2:
        if st.button("clear ↺"):
            # 상태 초기화 코드 수정
            for key in list(st.session_state.keys()):
                del st.session_state[key]  # 모든 세션 상태 삭제
            st.rerun() 
    
    st.subheader("이미지 파일에서 텍스트를 추출해줍니다.")
    st.subheader("광학문자인식(OCR) 기능을 이용합니다.")
    st.write("이미지(jpg, png...) 파일을 묶은 PDF에서 이미지 파일을 분리한 다음, 각 이미지에 포함된 글자들을 OCR로 추출합니다.")
    st.markdown("PDF 문서 파일에서 텍스트만 분리하시려면 [**PDF Extractor**](https://asadal-pdf.streamlit.app/)를 이용해주세요.")

    with st.container():
        pdf_file = st.file_uploader("PDF 파일을 업로드하세요.", type="pdf")
        img_file = st.file_uploader("이미지 파일을 업로드하세요.")

        if pdf_file:
            if 'final_txt' not in st.session_state:
                with st.spinner("텍스트를 추출하고 있습니다..."):
                    with NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(pdf_file.getvalue())
                        pdf_filepath = tmp_file.name
                        images = convert_from_path(pdf_filepath)
                        final_txt = ''
                        for image in images:
                            text_string = extract_text_from_img(image)  # 이미지 객체 직접 전달
                            final_txt += text_string
                        # final_txt = process_line_breaks(pdf_filepath)
                        st.session_state['final_txt'] = final_txt
            output_text(st, st.session_state['final_txt'])

        elif img_file:
            if 'final_txt' not in st.session_state:
                with st.spinner("텍스트를 추출하고 있습니다..."):
                    with NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(img_file.getvalue())
                        img_filepath = tmp_file.name
                        final_txt = extract_text_from_img(img_filepath)
                        st.session_state['final_txt'] = final_txt
            output_text(st, st.session_state['final_txt'])
    st.divider()
    with st.container():
        st.subheader("텍스트 줄바꿈 정렬기")
        st.write("문단 내 줄바꿈을 제거하고 문단을 가지런히 정렬해줍니다. 두 번 이상 연속 줄바꿈한 단락은 수정하지 않습니다.")
        txt_file = st.file_uploader("TXT 파일을 업로드하세요.", type="txt")
        if txt_file:
            if 'modified_txt' not in st.session_state:
                # 임시 파일 생성 및 파일 경로 처리
                with NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
                    contents = txt_file.getvalue().decode("utf-8")
                    tmp_file.write(contents.encode("utf-8"))
                    tmp_file_path = tmp_file.name

                modified_file_path = process_line_breaks(tmp_file_path)

                with open(modified_file_path, 'r', encoding='utf-8') as file:
                    modified_txt = file.read()
                st.session_state['modified_txt'] = modified_txt
            output_text(st, st.session_state['modified_txt'])
if __name__ == "__main__":
    app()
