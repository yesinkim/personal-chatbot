import google.generativeai as genai
import streamlit as st
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.oauth2 import service_account

# 페이지 구성 설정
st.set_page_config(page_title="OCR", page_icon="📄", layout="wide")

# Google Cloud 자격 증명 환경 변수 설정
config = st.secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["google_cloud"]
)

# Google Cloud 설정 읽기
project_id = credentials.project_id
location = config["ocr"]["location"]
processor_id = config["ocr"]["processor_id"]
processor_version_id = config["ocr"]["processor_version_id"]
field_mask = "text,entities,pages.pageNumber"  # 반환받을 필드 선택 (옵션)

# Google API 키 읽기
API_KEY = config["ocr"]["GOOGLE_API_KEY"]


# 모델 로드 및 채팅 세션 시작
@st.cache_resource
def load_model():
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel("gemini-pro")


model = load_model()

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# 사이드바 페이지 네비게이션
st.sidebar.title("동렬의 OCR")
page = st.sidebar.radio("Go to", ["Main", "Upload PDF/Image", "About"])


def main_page():
    st.title("PDF/이미지 요약 시스템")
    st.write("현재 PDF는 15페이지 이하만 가능합니다.")


def upload_page():
    st.title("PDF/Image 파일 업로드 및 처리")

    # 파일 업로더 초기화
    uploaded_file = st.file_uploader(
        "Choose a PDF or Image file",
        type=["pdf", "png", "jpg", "jpeg"],
        key="file_uploader",
    )

    def process_document(uploaded_file, mime_type):
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(
            credentials=credentials, client_options=opts
        )
        name = client.processor_version_path(
            project_id, location, processor_id, processor_version_id
        )

        # 메모리에서 바로 파일 읽기
        image_content = uploaded_file.getvalue()
        raw_document = documentai.RawDocument(
            content=image_content, mime_type=mime_type
        )
        request = documentai.ProcessRequest(
            name=name, raw_document=raw_document, field_mask=field_mask
        )
        result = client.process_document(request=request)
        return result.document.text

    if uploaded_file is not None:
        with st.spinner("Processing document..."):
            # 파일 타입에 따른 MIME 타입 설정
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                mime_type = "application/pdf"
            elif file_type == "image/png":
                mime_type = "image/png"
            elif file_type == "image/jpeg":
                mime_type = "image/jpeg"
            else:
                st.error("지원되지 않는 파일 형식입니다.")
                return

            # PDF/이미지 텍스트 추출
            pdf_text = process_document(uploaded_file, mime_type)
            st.session_state.pdf_text = pdf_text  # 상태 저장
            st.session_state.response = None  # 응답 초기화
            st.success("Document processed successfully.")

    def handle_user_input():
        if "pdf_text" in st.session_state:
            # PDF 내용과 사용자 입력 결합
            query = (
                st.session_state.pdf_text
                + " "
                + st.session_state.user_input
                + " 에 대해서 정리하고 요약해줘."
            )
            with st.spinner("Generating response..."):
                response = model.generate_content(query)
                st.session_state.response = response.text  # 응답을 세션 상태에 저장

    # 사용자 입력 받기
    st.text_input(
        "추가로 입력할 메시지를 작성해주세요:",
        key="user_input",
        on_change=handle_user_input,
    )

    # 응답 표시 및 초기화 버튼
    if "response" in st.session_state and st.session_state.response:
        st.write(st.session_state.response)
        if st.button("다시 질문하기"):
            del st.session_state.pdf_text
            del st.session_state.user_input
            del st.session_state.response
            st.experimental_rerun()


def about_page():
    st.title("About")
    st.write("pdf, 이미지 요약/풀이 사이트입니다.")
    st.write("Developed by [백동렬].")
    st.write("Version 1.0")


# 페이지 라우팅
if page == "Main":
    main_page()
elif page == "Upload PDF/Image":
    upload_page()
elif page == "About":
    about_page()
