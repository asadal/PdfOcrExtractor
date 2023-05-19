import os
import PyPDF3
import streamlit as st
import tempfile as tf
from tempfile import NamedTemporaryFile
import pytesseract
from tqdm import tqdm
from pdf2image import convert_from_path
import cv2

def get_tmp_filepath(uploaded_file):
    with NamedTemporaryFile(delete=True) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_filepath = tmp_file.name
        print("temporary_filepath : ", tmp_filepath)
        return tmp_filepath
def extract_text_from_img(img_path):
    text_string = pytesseract.image_to_string(img_path, lang='kor+eng').strip()
    print(text_string)
    return text_string

def output_text(st, final_txt):
    st.header("추출된 텍스트")
    st.text_area("", value=final_txt, height=500)
    # 추출된 텍스트를 txt 파일로 다운로드
    st.header("텍스트 다운로드")
    st.download_button(
        label="📥 Download Timeline Script ⏱",
        data=final_txt,
        file_name='extracted_text.txt',
        mime='text/plain'
    )

def app():
    # Set page title and icon
    st.set_page_config(
        page_title="PDF Extractor",
        page_icon="https://img.uxwing.com/wp-content/themes/uxwing/download/file-folder-type/download-pdf-icon.svg"
    )

    # Featured image
    st.image(
        "https://img.uxwing.com/wp-content/themes/uxwing/download/file-folder-type/download-pdf-icon.svg",
        width=120
    )

    # Main title and description
    st.title("텍스트 추출기")
    st.subheader("이미지 파일에서 텍스트를 추출해줍니다.")
    st.subheader("광학문자인식(OCR) 기능을 이용합니다.")
    st.write("이미지(jpg, png...) 파일을 묶은 PDF에서 이미지 파일을 분리한 다음, 각 이미지에 포함된 글자들을 OCR로 추출합니다.")
    st.markdown("PDF 문서 파일에서 텍스트만 분리하시려면 *[PDF Extractor](https://asadal-pdf.streamlit.app/)*를 이용해주세요.")
    
    if 'key' not in st.session_state:
        st.session_state['key'] = 'value'
    
    pdf_file = st.file_uploader("PDF 파일을 업로드하세요.", type="pdf", key='pdf_file')
    
    st.divider()
    
    img_file = st.file_uploader("이미지 파일을 업로드하세요.")
    
    st.divider()
    
    if pdf_file is not None:
        try:
#             os.system("brew install tesseract tesseract-lang && brew link tesseract")
            with st.spinner("텍스트를 추출하고 있습니다..."):
                with NamedTemporaryFile(delete=True) as tmp_file:
                    tmp_file.write(pdf_file.getvalue())
                    pdf_filepath = tmp_file.name
                    print("temporary_filepath : ", pdf_filepath)
                    final_txt = ""
                    images = convert_from_path(pdf_filepath)
                    print("전체 페이지 수 : ", len(images))
                    for i, image in enumerate(images):
                        image.save(pdf_filepath + f"page_{i+1}.jpg", "JPEG")
                        img = cv2.imread(pdf_filepath + f"page_{i+1}.jpg")
                        text_string = extract_text_from_img(img)
                        final_txt += text_string
        except Exception as e:
            st.error("오류가 발생했습니다. 😥")
            st.error(e)
        
        output_text(st, final_txt)
        pdf_file.__del__()
        
    elif img_file is not None:
        try:
#             os.system("brew install tesseract tesseract-lang && brew link tesseract")
            with st.spinner("텍스트를 추출하고 있습니다..."):
                with NamedTemporaryFile(delete=True) as tmp_file:
                    tmp_file.write(img_file.getvalue())
                    img_filepath = tmp_file.name
                    print("temporary_filepath : ", img_filepath)
                    final_txt = ""
                    text_string = extract_text_from_img(img_filepath)
                    final_txt += text_string
        except Exception as e:
            st.error("오류가 발생했습니다. 😥")
            st.error(e)
        
        output_text(st, final_txt)
        img_file.__del__()
        
    else:
        st.write("파일을 업로드하거나 끌어다 놓으세요.")
        st.stop()
        
if __name__ == "__main__":
    app()
