import os
import PyPDF3
import streamlit as st
import tempfile as tf
from tempfile import NamedTemporaryFile
import pytesseract
from tqdm import tqdm
from pdf2image import convert_from_path
import cv2

def extract_text_from_img(img):
    text_string = pytesseract.image_to_string(img, lang='kor+eng').strip()
    return text_string

def output_text(st, final_txt):
    st.header("추출된 텍스트")
    st.text_area("", value=final_txt, height=500)
    st.header("텍스트 다운로드")
    st.download_button(
        label="📥 Download Timeline Script ⏱",
        data=final_txt,
        file_name='extracted_text.txt',
        mime='text/plain'
    )

def app():
    st.set_page_config(page_title="PDF Extractor", page_icon="https://cdn-icons-png.flaticon.com/512/29/29099.png")
    st.image("https://cdn-icons-png.flaticon.com/512/29/29099.png", width=120)
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("텍스트 추출기")
    with col2:
        if st.button("clear ↺"):
            st.session_state.clear()  # 상태 초기화
            st.experimental_rerun()  # 재실행
    
    st.subheader("이미지 파일에서 텍스트를 추출해줍니다.")
    st.subheader("광학문자인식(OCR) 기능을 이용합니다.")
    st.write("이미지(jpg, png...) 파일을 묶은 PDF에서 이미지 파일을 분리한 다음, 각 이미지에 포함된 글자들을 OCR로 추출합니다.")
    st.markdown("PDF 문서 파일에서 텍스트만 분리하시려면 [**PDF Extractor**](https://asadal-pdf.streamlit.app/)를 이용해주세요.")

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

if __name__ == "__main__":
    app()
