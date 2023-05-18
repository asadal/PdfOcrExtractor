import os
import PyPDF3
import streamlit as st
import tempfile as tf
from tempfile import NamedTemporaryFile
import pdfplumber
import pytesseract
from tqdm import tqdm
# from PIL import Image
from wand.image import Image
# from wand.image import Color as WandColor

def create_temp_dir():
    # Create a temporary directory
    set_temp_dir = tf.TemporaryDirectory()
    temp_dir = set_temp_dir.name + "/"
    # 디렉터리 접근 권한 설정
    os.chmod(temp_dir, 0o700)
    return temp_dir

def get_page_numbers(pdf_file):
    pdfReader = PyPDF3.PdfFileReader(pdf_file)
    pages = pdfReader.numPages
    return pages

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
    st.title("PDF Extractor")
    st.subheader("Extract text from a PDF file.")

    pdf_file = st.file_uploader("PDF 파일을 업로드하세요.", type="pdf")
    if pdf_file is not None:
        # temp_dir = create_temp_dir()
        # pdf_filename = pdf_file.name
        # pdf_filepath =  temp_dir + pdf_filename
        # print("temp_dir + filename : ", temp_dir + pdf_filename)
        # os.environ['MAGICK_HOME'] = '/opt/homebrew/bin/magick/imagemagick/7.1.1-9'

        with st.spinner("텍스트를 추출하고 있습니다..."):
            with NamedTemporaryFile(suffix="mp3", delete=False) as tmp_file:
                tmp_file.write(pdf_file.getvalue())
                pdf_filepath = tmp_file.name
                print("pdf_filepath : ", pdf_filepath)
                final_txt = ""
                with pdfplumber.open(pdf_filepath) as pdf:
                    pdf_pages = get_page_numbers(pdf_filepath)
                    for num in tqdm(range(0, pdf_pages)):
                        page = pdf.pages[num]
                        img_path = page.to_image(resolution=300).convert('L').save(filename=pdf_filepath+f"page_{num}.png")
                        txt = pytesseract.image_to_string(Image.open(img_path))
                        final_txt += txt

        # 텍스트 출력
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

if __name__ == "__main__":
    app()
