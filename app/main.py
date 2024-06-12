import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title

def page_view():
    # add_page_title()
    show_pages(
        [
            Page("app/main.py", "Introduce", is_section=True),
            Page(
                "app/pages/SYU-GPT.py",
                "SYU-GPT",
                ":globe_with_meridians:",
                in_section=True,
            ),
            Page(
                "app/pages/OCR.py",
                "문서 및 이미지 요약",
                ":page_facing_up:",
                in_section=True,
            ),
            Page(
                "app/pages/음식추천.py", "음식추천", ":fork_and_knife:", in_section=True
            ),
        ]
    )

page_view()

st.markdown(
    """
<style>
.stTitle {
    font-size: 3em;
    font-weight: bold;
    color: #228B22; /* Dark green color */
    text-align: center;
    margin-bottom: 20px;
}

.stProjectInfo {
    text-align: center;
    margin-bottom: 15px;
}

.stProjectInfo h3 {
    font-size: 1.5em;
    font-weight: bold;
}

.stProjectInfo p {
    font-size: 1.2em;
}

.stTeamList {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}

.stTeamMember {
    margin: 0 10px;
    padding: 10px;
    border-radius: 5px;
    text-align: center;
    width: 200px;
}

.stTeamMember h4 {
    margin-top: 0;
    margin-left: 25px;
}

.stTeamMember a {
    display: block;
    margin-top: 5px;
    text-decoration: none;
    color: gray; 

.stTeamMember a:hover {
    text-decoration: underline;
}

.stTeamMember a i {
    margin-right: 5px; /* 아이콘과 텍스트 사이 간격 */
}

.stProjectDetails {
    display: flex;
    justify-content: center;
}

.stProjectDetail {
    margin: 0 20px;
    padding: 10px;
    border-radius: 5px;
    width: 300px;
}

.stProjectDetail h3 {
    margin-top: 0;
}

.stProjectDetail a {
    display: block;
    margin-top: 5px;
    text-decoration: none;
    color: gray
}

.stProjectDetail a:hover {
    text-decoration: underline;
}
</style>
<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1 class='stTitle'>Personal Chatbot</h1>", unsafe_allow_html=True)

st.markdown(
    """
    <div class='stProjectInfo'>
        <p>이 프로젝트는 삼육대학교 SW중심대학사업단에서 진행하는 2024년도 1학기 산학연계 프로젝트입니다. 멘토와 멘티로 팀을 구성해 LLM을 챗봇 시스템을 개발합니다.</p>
        <h3>프로젝트 진행기간</h3>
        <p>2024.03.19 ~ 2024.06.17(예정)</p>
        <h3>프로젝트 개요</h3>
        <p>이 프로젝트는 LangChain을 활용한 LLM(대형 언어 모델) 프롬프트 엔지니어링과 RAG(검색 증강 생성) 기술을 이해하고 활용하는 것을 목표로 하며, Streamlit을 통해 유저 인터페이스 및 입출력 시각화를 구현합니다.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class='stTeamList'>
        <div class='stTeamMember'>
            <h4>김소원</h4>
            <a href="https://github.com/shine515"><i class="fab fa-github"></i> GitHub</a>
            <a href="https://syu-chatbot.streamlit.app/음식추천" target="_self"><i class="fas fa-link"></i> 음식추천 챗봇</a>
        </div>
        <div class='stTeamMember'>
            <h4>백동렬</h4>
            <a href="https://github.com/think0507"><i class="fab fa-github"></i> GitHub</a>
            <a href="https://syu-chatbot.streamlit.app/%EB%AC%B8%EC%84%9C%20%EB%B0%8F%20%EC%9D%B4%EB%AF%B8%EC%A7%80%20%EC%9A%94%EC%95%BD" target="_self"><i class="fas fa-link"></i> 문서 및 이미지 요약 챗봇</a>
        </div>
        <div class='stTeamMember'>
            <h4>양이찬</h4>
            <a href="https://github.com/y2chan"><i class="fab fa-github"></i> GitHub</a>
            <a href="https://syu-chatbot.streamlit.app/SYU-GPT" target="_self"><i class="fas fa-link"></i> 삼육대학교 GPT 챗봇</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
