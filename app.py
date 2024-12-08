from dataclasses import dataclass
from typing import Literal
import streamlit as st
import streamlit.components.v1 as components
import requests
import random
import time

# Настройки Streamlit
st.set_page_config(
    page_title="Чат-бот LLM",
    page_icon="static/favicon.png",
    layout="centered"
)

API_URL = "https://api-inference.huggingface.co/models/csebuetnlp/mT5_multilingual_XLSum"
API_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

@dataclass
class Message:
    # Class for keeping track of a chat message.
    origin: Literal["human", "ai"]
    message: str

def query_huggingface_api(prompt: str) -> str:
    # Отправляет запрос к API Hugging Face и возвращает ответ модели.
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()[0]['summary_text']
    else:
        st.error(f"Ошибка API Hugging Face: {response.status_code}")
        return "Ошибка при запросе к модели."

def load_css():
    with open("static/styles.css", "r") as file:
        css = f"<style>{file.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []

def on_click_callback():
    human_prompt = st.session_state.human_prompt
    llm_response = query_huggingface_api(human_prompt)
    st.session_state.history.append(Message("human", human_prompt))
    st.session_state.history.append(Message("ai", llm_response))

load_css()
initialize_session_state()

# Загрузка спиннер-экрана
with open("static/loading.html", "r") as file:
        loading_html = file.read()

html_placeholder = st.empty()
html_placeholder.markdown(loading_html, unsafe_allow_html=True)
time.sleep(3)
html_placeholder.empty()



# Добавляем видео в качестве фона
st.markdown("""
<video class="background-video" autoplay muted loop>
    <source src="app/static/background_video.mp4" type="video/mp4">
    Ваш браузер не поддерживает воспроизведение видео.
</video>
""", unsafe_allow_html=True)

# Бургер-меню
st.markdown("""
<div class="burger-menu">
    <span></span>
    <span></span>
    <span></span>
</div>
""", unsafe_allow_html=True)

# Реализация чат-бота
st.title("Чат-бот")
chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")
credit_card_placeholder = st.empty()

with chat_placeholder:
    st.markdown("""
    <div class="chat-row">
        <img class="chat-icon" src="app/static/ai_icon.png">
        <div class="chat-bubble ai-bubble">
            Привет! Чем могу помочь?
        </div>
    </div>
    """, unsafe_allow_html=True)
        
    for chat in st.session_state.history:
        div = f"""
        <div class="chat-row 
            {'' if chat.origin == 'ai' else 'row-reverse'}">
            <img class="chat-icon" src="app/static/{
                'ai_icon.png' if chat.origin == 'ai' 
                            else 'user_icon.png'}">
            <div class="chat-bubble
            {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}">
                {chat.message}
            </div>
        </div>
        """
        st.markdown(div, unsafe_allow_html=True)
    
    for _ in range(3):
        st.markdown("")

with prompt_placeholder:
    st.markdown("""<h3>Введите ваш запрос:</h3>""", unsafe_allow_html=True)
    cols = st.columns((5, 1))
    cols[0].text_area(
        "Чат",
        value="",
        label_visibility="collapsed",
        key="human_prompt",
        height=100
    )
    cols[1].form_submit_button(
        "Отправить", 
        type="primary", 
        on_click=on_click_callback,
    )

credit_card_placeholder.caption(f"""
Debug: 
{[msg.message for msg in st.session_state.history]}
""")

components.html(
    """
    <script>

    const streamlitDoc = window.parent.document;

    const buttons = Array.from(
        streamlitDoc.querySelectorAll('.stButton > button')
    );
    const submitButton = buttons.find(
        el => el.innerText === 'Submit'
    );

    document.addEventListener('DOMContentLoaded', () => {
      const burgerMenu = document.querySelector('.burger-menu');
      
      burgerMenu.addEventListener('click', () => {
          burgerMenu.classList.toggle('active');
      });
    });
   
    document.addEventListener('DOMContentLoaded', function() {
        const textareas = window.parent.document.querySelectorAll('.stTextArea textarea');
        textareas.forEach(textarea => {
            textarea.setAttribute('placeholder', 'Ваше место для текста');
        });
    });
                    
    streamlitDoc.addEventListener('keydown', function(e) {
        switch (e.key) {
            case 'Enter':
                submitButton.click();
                break;
        }
    });

    </script>
    """,
    height=0,
    width=0
)
