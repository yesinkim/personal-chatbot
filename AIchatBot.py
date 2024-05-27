#AIchatBot.py
import google.generativeai as genai
import streamlit as st
import time as tm

st.set_page_config(layout="wide")

genai.configure(api_key="AIzaSyAMvYvK7i5DwFXaPynEg14ZVWt_C8Ye-1s")

# Set up the model
generation_config = {
  "temperature": 2,
  "top_p": 0.7,
  "top_k": 1,
  "max_output_tokens": 700,
}

def load_model():
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config
                              )
    print("model loaded...")
    return model

model = load_model()
#convo = model.start_chat(history=[])

#convo.send_message("YOUR_USER_INPUT")
#print(convo.last.text)
Title = st.columns(1)
ChatBot, Prompt_Q = st.columns([6,4])

if "chat_session" not in st.session_state:
    st.session_state["chat_session"] = model.start_chat(history=[]) # ChatSession 반환
setProm = ("너의 역할은 내가 주는 조건에 맞는 음식을 3가지 이하로 추천해 주는 거고, "
           "각 음식에 대한 설명은 2문장 이하로 적어줘. 레시피는 요청하는 경우에만 알려줘. "
           "내가 한 질문은 답변에 포함시키지 마"
           "음식 별로 깔끔하게 정돈 된 답변을 줘"
           "답변 초반에 원하시는 조건의 음식들을 찾아봤어요. 이 음식은 어떠신가요? 같은 친절한 문구와 귀여운 이모티콘을 추가해 줘"
           "음식 리스트가 나오면 그 음식이 조건에 부합한지 한번 더 확인한 후 답변해줘"
           "답변의 마지막에 음식의 레시피를 알려줄 수 있다는 안내문구를 추가해 줘"
           "만약 음식 추천, 레시피를 묻는 것과 관련없는 질문을 한다면 음식추천과 관련되지 않은 질문에는 "
           "답 할 수 없다고 말해.")

#for content in st.session_state.chat_session.history:
    
    #if content < 1: 
st.session_state.chat_session.send_message(setProm)

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

##############################################
with ChatBot:
    st.header("음식추천챗봇")
    if prompt := st.chat_input("메시지를 입력하세요."):    
        with st.chat_message("user"):
            st.markdown(prompt)    
        with st.chat_message("ai"):        
            message_placeholder = st.empty() # DeltaGenerator 반환
            full_response = ""
            with st.spinner("메시지 처리 중입니다."):
                try :
                    response = st.session_state.chat_session.send_message(prompt, stream = True)
                except:
                    for chunk in "잠시 후에 다시 시도해주세요!":            
                        full_response += chunk
                        message_placeholder.markdown(full_response)
                for chunk in response:            
                    full_response += chunk.text
                    message_placeholder.markdown(f'{full_response}') 


with Prompt_Q :
    with st.form(key='my_form'): 
        genre =st.radio('음식 장르 선택',['미정','분식','한식','양식','일식','중식'])
        flavor=st.multiselect('원하는 맛 선택(부정의 경우 앞에 <안> 배치)', ['달콤한', '매운', '짠', '신', '안'])
        cook =st.multiselect('조리 방식 선택', ['국','탕','찌개','찜', '구이', '볶음', '튀김', '스프','베이킹'])
        time =st.multiselect('식사시간 선택', ['아침 식사', '점심 식사', '저녁 식사','간식'])
        stuff=st.multiselect('재료 선택', ['밥', '빵', '면','떡','과일', '야채', '어류', '고기','갑각류'])
        deliver=st.multiselect('직접조리 or 배달/포장(조리된 음식 구입)', ['직접요리', '조리된 음식 구입'])
        push = st.form_submit_button(label='음식 추천 받기')
        
                
def sent():
    #st.session_state["chat_session"] = model.start_chat(history=[]) # ChatSession 반환
    
    prompt =''
    if genre == '미정':
        prompt = '어떤 음식이든'
    else:
        prompt = (f'{genre}중에 ')
    if flavor:
        prompt += (f'{flavor}거 ')
    if cook:
        prompt += (f'{cook}으로 조리하고 ')
    if time:
        prompt += (f'{time}으로 먹기 좋은 ')
    if stuff:
        prompt += (f'{stuff}가 들어간 ')
    if deliver:
        prompt += (f'{deliver}로 먹을 수 있는')
    prompt +=('음식을 추천해 줘')
        
    with st.chat_message("ai"):
        message_placeholder = st.empty() # DeltaGenerator 반환
        full_response = ""
        with st.spinner("메시지 처리 중입니다."):
            try :
                response = st.session_state.chat_session.send_message(prompt, stream = True)
            except:
                for chunk in "잠시 후에 다시 시도해주세요!":            
                    full_response += chunk
                    message_placeholder.markdown(full_response)
            full_response = ""
            for chunk in response:            
                full_response += chunk.text
                message_placeholder.markdown(full_response)
    
    

if push:
    with ChatBot:
        sent()
                    
    
        
