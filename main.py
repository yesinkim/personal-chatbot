import os
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
import logging
from langchain_community.document_loaders import DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap
from langchain_google_genai import ChatGoogleGenerativeAI

VECTOR_STORE_PATH = "data/vector_store.faiss"

# 환경 설정
def setup_environment():
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_TOKEN")
    os.environ["LANGCHAIN_PROJECT"] = "SYU-GPT"
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# 문서 처리 준비
@st.cache_resource
def generate_response(user_input):
    try:
        # 파일별 설정
        config = {
            'introduce.txt': {'chunk_size': 1500, 'chunk_overlap': 300},
            '관련 링크 data.txt': {'chunk_size': 1500, 'chunk_overlap': 300},
            '교통 data.txt': {'chunk_size': 1500, 'chunk_overlap': 300},
            '도서관 data.txt': {'chunk_size': 2000, 'chunk_overlap': 300},
            '동아리 data.txt': {'chunk_size': 4500, 'chunk_overlap': 300},
            '등록 data.txt': {'chunk_size': 2000, 'chunk_overlap': 300},
            '성적 data.txt': {'chunk_size': 1500, 'chunk_overlap': 300},
            '셔틀버스 data.txt': {'chunk_size': 1000, 'chunk_overlap': 300},
            '수강신청 data.txt': {'chunk_size': 1500, 'chunk_overlap': 250},
            '시설 정보 data.txt': {'chunk_size': 2000, 'chunk_overlap': 350},
            '업무별 전화번호 data.txt': {'chunk_size': 1000, 'chunk_overlap': 200},
            '장학금 data.txt': {'chunk_size': 4000, 'chunk_overlap': 100},
            '졸업 data.txt': {'chunk_size': 1200, 'chunk_overlap': 250},
            '증명서 data.txt': {'chunk_size': 2000, 'chunk_overlap': 250},
            '학과 data.txt': {'chunk_size': 7000, 'chunk_overlap': 500},
            '학사 일정 data.txt': {'chunk_size': 1500, 'chunk_overlap': 200},
            '후문 정보 data.txt': {'chunk_size': 2000, 'chunk_overlap': 300},
            '학교 건물 data.txt': {'chunk_size': 3000, 'chunk_overlap': 100},
        }

        # HuggingFaceEmbeddings 객체 생성
        model_name = "jhgan/ko-sbert-nli"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        hf = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        if os.path.exists(VECTOR_STORE_PATH):
            # 저장된 vector store가 있으면 이를 불러옵니다.
            docsearch = FAISS.load_local(VECTOR_STORE_PATH, hf, allow_dangerous_deserialization=True)
        else:
            # DirectoryLoader로 모든 txt 파일 로드
            loader = DirectoryLoader(".", glob="data/SYU_GPT/*.txt", show_progress=True)
            docs = loader.load()
            all_splits = []
            for doc in docs:
                file_path = doc.metadata['source']
                file_name = os.path.basename(file_path)
                if file_name in config:
                    chunk_size = config[file_name]['chunk_size']
                    chunk_overlap = config[file_name]['chunk_overlap']
                else:
                    chunk_size = 1500
                    chunk_overlap = 300
                text_splitter = CharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                splits = text_splitter.split_documents([doc])
                all_splits.extend(splits)
            # 모든 분할이 완료된 후에 한 번만 vectorstore를 생성
            if all_splits:
                docsearch = FAISS.from_documents(all_splits, hf)
                # 생성된 vector store를 로컬에 저장합니다.
                docsearch.save_local(VECTOR_STORE_PATH)
            else:
                print("No documents were split or processed.")
                return "문서 처리가 완료되지 않았습니다."

        retriever = docsearch.as_retriever(
            search_type="mmr",
            search_kwargs={'k': 3, 'fetch_k': 10})
        retriever.get_relevant_documents("혁신성장 정책금융에 대해서 설명해줘")
        template = """당신의 이름은 SYU-GPT입니다. 삼육대학교에 대한 다양한 정보들을 제공하는 챗봇입니다.
                    All answers are based on the introduce.txt file.
                    Please introduce yourself when the questioner greets you.
                    Please introduce yourself when the questioner says "Hi", "Hello", "안녕".
                    너는 학과, 장학금, 등록, 성적, 졸업, 수강신청, 셔틀버스, 교통, 시설정보, 학사일정, 도서관, 학교 건물, 증명서, 후문 정보, 동아리 등 다양한 주제의 정보를 제공합니다.
                    The database consists of detailed information in each category's txt file.
                    Your answers should be delivered in an accurate, informative, and friendly dialogue style.
                    They should also be written in bullet style format.
                    URLs to various homepages must be spaced one space at the end.
                    When you tell me the URL, don't skip it and tell me the whole thing.
                    Don't make up anything that's not relevant to what you asked.
                    Please ensure the information provided is up to date and relevant to the user's query and files.
                    You always refers to factual statements that can be referenced.
                    You says only facts related to 삼육대학교 and does not add information on its own.:
        {context}
        
        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, max_tokens=2048)
        chain = RunnableMap({
            "context": lambda x: retriever.get_relevant_documents(x['question']),
            "question": lambda x: x['question']
        }) | prompt | llm
        response = chain.invoke({'question': user_input}).content
        return response
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"오류가 발생했습니다: {str(e)}"

def main():
    st.set_page_config(
        page_title="SYU-GPT",
        # page_icon="😃",
        page_icon="photo/Logo.png",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "https://www.extremelycoolapp.com/bug",
        }
    )
    setup_environment()
    st.title('SYU-GPT', anchor=False)
    # 먼저, subheader와 caption을 포함하는 부분을 st.empty()를 사용하여 빈 홀더로 만듭니다.
    info_placeholder = st.empty()
    # 이제 info_placeholder를 사용하여 subheader와 caption을 표시합니다.
    with info_placeholder.container():
        st.subheader('삼육대학교 검색 엔진', anchor=False)
        st.caption('여러분이 검색하고 싶은 학교 정보를 검색하세요!')
        st.caption('데이터를 주기적으로 업데이트 중입니다.')
        st.caption('삼육대학교 재학생이라면 사용해보세요! 😊')
        st.caption(' ')
        st.caption('사용하시는데 불편한 점이 있으면 아래 사용 가이드를 참고해보세요!')
        st.caption(' ')
        st.page_link("pages/guide.py", label="사용 가이드 바로가기", help="사용 가이드로 이동합니다.", icon="▶")
        st.caption(' ')
        st.markdown('**안녕! 이라고 인사해보세요 ✋✋**')
    # 사이드바
    st.sidebar.image("photo/syugptLogo.png")
    hide_img_fs = '''
    <style>
    button[title="View fullscreen"]{
        visibility: hidden;}
    </style>
    '''
    st.sidebar.markdown(hide_img_fs, unsafe_allow_html=True)
    st.sidebar.write('-' * 50)
    st.sidebar.subheader("Menu")
    st.sidebar.page_link("main.py", label="Home", help="홈 화면으로 이동합니다", icon="🏠")
    st.sidebar.page_link("pages/greeting.py", label="Greeting", icon="✋")
    st.sidebar.page_link("pages/guide.py", label="User's Guide", icon="❓")
    st.sidebar.subheader("Other Web")
    st.sidebar.page_link("https://www.syu.ac.kr/", label="Sahmyook University", help="삼육대학교 공식 사이트로 이동합니다")
    st.sidebar.page_link("https://chat.openai.com/", label="ChatGPT", help="Chat GPT 사이트로 이동합니다")
    st.sidebar.page_link("https://gabean.kr/", label="GaBean", help="개발자의 또 다른 웹 사이트로 이동합니다")
    if "chat_session" not in st.session_state:
        st.session_state.messages = []
    if user_input := st.chat_input("질문을 입력하세요."):
        info_placeholder.empty()
        try:
            with st.spinner("답변을 생성하는 중입니다..."):
                response = generate_response(user_input)
            if response.startswith("오류가 발생했습니다:"):
                st.error(response)
            else:
                with st.chat_message("user", avatar="🧃"):
                    st.markdown(user_input)
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("SYU-GPT", avatar="photo/Logo.png"):
                    st.markdown(response)
                    st.caption(' ')
                    st.caption('사용하시는데 불편한 점이 있으면 아래 사용 가이드를 참고해보세요!')
                    st.caption(' ')
                    st.page_link("pages/guide.py", label="사용 가이드 바로가기", help="사용 가이드로 이동합니다.", icon="▶")
                st.session_state.messages.append({"role": "SYU-GPT", "content": response})
        except Exception as e:
            st.error("에러가 발생했습니다: {}".format(e))
if __name__ == "__main__":
    main()
