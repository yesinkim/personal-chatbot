import json
import google.generativeai as genai
import streamlit as st
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.oauth2 import service_account

# Streamlit에서 비밀 정보 로드
config = st.secrets

# JSON 문자열을 Python 딕셔너리로 변환
credentials_info = json.loads(config["google_cloud"]["credentials"])

# 자격 증명 생성
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Google Cloud 설정 읽기
project_id = credentials.project_id
location = config["google_cloud"]["location"]
processor_id = config["google_cloud"]["processor_id"]
processor_version_id = config["google_cloud"]["processor_version_id"]
field_mask = "text,entities,pages.pageNumber"  # 반환받을 필드 선택 (옵션)

# Google API 키 읽기
api_key = config["ocr"]["GOOGLE_API_KEY"]

# 모델 로드 및 채팅 세션 시작
@st.cache_resource
def load_model():
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        return model
    except Exception as e:
        st.error(f"모델 로드 실패: {str(e)}")
        return None

model = load_model()

if model and "chat_session" not in st.session_state:
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
        try:
            opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
            client = documentai.DocumentProcessorServiceClient(credentials=credentials, client_options=opts)
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
        except Exception as e:
            st.error(f"문서 처리 실패: {str(e)}")
            return None

    if uploaded_file is not None:
        with st.spinner("Processing document..."):
            # 파일 타입에 따른 MIME 타입 설정
            file_type = uploaded_file.type
            mime_type = file_type if file_type in ["application/pdf", "image/png", "image/jpeg"] else None

            if mime_type is None:
                st.error("지원되지 않는 파일 형식입니다.")
                return

            # PDF/이미지 텍스트 추출
            pdf_text = process_document(uploaded_file, mime_type)
            if pdf_text:
                st.session_state.pdf_text = pdf_text  # 상태 저장
                st.session_state.response = None  # 응답 초기화
                st.success("Document processed successfully.")
                print(f"Extracted text: {pdf_text}")  # 터미널에 결과 출력
            else:
                st.error("문서 처리에 실패했습니다.")

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
                try:
                    response = model.generate_content(query)
                    st.session_state.response = response.text  # 응답을 세션 상태에 저장
                    print(f"Generated response: {response.text}")  # 터미널에 결과 출력
                except Exception as e:
                    st.error(f"응답 생성 실패: {str(e)}")

    if uploaded_file is not None:
        st.text_input("추가로 입력할 메시지를 작성해주세요:", key="user_input")

        if st.button("Generate Response"):
            handle_user_input()

    # 응답 표시 블럭 생성 및 초기화 버튼
    response_container = st.container()

    with response_container:
        if "response" in st.session_state and st.session_state.response:
            st.subheader("Generated Response")
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
