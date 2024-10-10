import streamlit as st
import os, utils, opik
from groq import Groq

# --- API Key 설정 -------------------------------------------------------------
# Groq API 키 설정
GROQ_API_KEY = st.secrets['GROQ_API_KEY'] 
# Comet API 키 설정
OPIK_API_KEY = st.secrets['OPIK_API_KEY'] 

# Groq 초기화
client = Groq(api_key=GROQ_API_KEY)

# Opik 클라이언트 객체 생성 
# 이후에 trace와 span 객체 생성에 이 클라이언트를 사용하게 된다.
opik_client = opik.Opik()

# Comet Opik을 설정
opik.configure(
    api_key=st.secrets(OPIK_API_KEY),
    workspace='ontology'
)

# Comet Opik 프로젝트에 연결
# Comet Opik 프로젝트와 연결하면 모델의 학습 과정이나 결과를 기록하고 관리할 수 있게 해준다.
os.environ['OPIK_PROJECT_NAME'] = 'Wizard Chatbot Demo'  

# --- 마법 아이템 목록 ------------------------------------------------------------
# 마법 상점에서 판매할 마법 아이템 목록을 문자열로 정의한다.
# 이 아이템 목록은 상점에서 판매할 마법 물품에 대한 정보를 포함하고 있다.
product_list = '''# 마법 상점 재고 목록

## 물약:
- 치유 물약
  - 가격: 10 금화
  - 효과: HP 50 회복
  - 구매 가능성: 높음(아이템을 쉽게 구할 수 있음)

- 투명화 물약
  - 가격: 30 금화
  - 효과: 5분 동안 투명화
  - 구매 가능성: 희귀(아이템을 거의 구할 수 없음)

## 마법 지팡이:
- 불의 지팡이
  - 가격: 50 금화
  - 효과: 화염구 주문 발사
  - 구매 가능성: 보통(아이템을 상당히 자주 구할 수 있음)

- 번개의 지팡이
  - 가격: 70 금화
  - 효과: 번개 주문 발사
  - 구매 가능성: 낮음(아이템을 가끔 구할 수 있음)

## 마법 유물:
- 보호의 반지
  - 가격: 40 금화
  - 효과: 방어력 +5
  - 구매 가능성: 보통(아이템을 상당히 자주 구할 수 있음)

- 지혜의 부적
  - 가격: 100 금화
  - 효과: 지능 10 포인트 증가
  - 구매 가능성: 희귀(아이템을 거의 구할 수 없음)
'''

# --- 챗봇의 System Message 설정 --------------------------------------------------
SYSTEM_MESSAGE = f'''당신은 마법사 상점, Arcane Emporium의 AI 어시스턴트인 \
WizardBot입니다.

당신의 역할은 고객이 마법 아이템을 탐색하고, 그 효과에 대한 정보를 제공하며, \
구매 과정을 안내하는 것입니다.

Arcane Emporium은 물약, 마법 지팡이, 마법 유물 등 다양한 마법 제품을 제공합니다.

고객의 마법적인 필요에 대해 질문하고, 아이템을 추천하며, 비밀 프로모션이나 \
희귀 아이템 출현에 대해 알릴 수 있습니다.

현재 재고 목록은 다음과 같습니다:

```{product_list}```

환영 인사는 처음 한번만 하세요. 마법 같은 쇼핑 경험을 제공하고, 고객이 \
궁금한 점이 있거나 마법적인 도움이 필요할 때 언제든지 문의할 수 있도록 \
안내하십시오. 신비롭고 매력적이며 친근한 스타일로 대답합니다.\
'''

GREETINGS = '''✨ 환영합니다, 존경하는 마법사! ✨

Arcane Emporium에 오신 것을 환영합니다. 

저는 WizardBot, 이 신비로운 상점의 AI 어시스턴트입니다. 

어떤 마법 같은 아이템을 찾고 계신가요? 

물약, 마법 지팡이, 유물... 혹은 아직 꿈꾸는 특별한 아이템이 있을지도 몰라요. 

궁금한 점이 있거나 도움이 필요하면 언제든지 저에게 물어보세요. 

Arcane Emporium에서 마법의 세계로 떠나보세요! 💫 
'''

# 시스템 메시지와 인사말을 설정한다.
context = [
    {'role': 'system', 'content': SYSTEM_MESSAGE},
    {'role': 'assistant', 'content': GREETINGS}
]

# --- Streamlit 구성 -----------------------------------------------------------
# 메인 화면에 타이틀과 캡션을 설정한다.
st.title('마법사 상점 Arcane Emporium')    # 웹 애플리케이션의 제목을 설정한다.
st.caption('AI 쇼핑 어시스턴트입니다.')       # 설명 문구(부제목)를 추가한다.

# AI 챗봇이 먼저 인사말을 한다.
st.chat_message(name='ai').write(GREETINGS)

# 세션 상태에 'messages' 키가 없으면 빈 리스트로 초기화한다.
if 'messages' not in st.session_state:  
    st.session_state['messages'] = []

# 세션 상태에 저장한 메시지를 화면에 출력한다.
for msg in st.session_state.messages:  
    st.chat_message(msg['role']).write(msg['content'])  

# 사용자 입력을 처리하고 LLM 모델의 응답을 생성한다.
if prompt := st.chat_input():  
    # 사용자 입력을 대화 기록에 추가한다.  
    st.session_state['messages'].append({'role': 'user', 'content': prompt}) 
    # 화면에 사용자 입력을 출력한다.
    st.chat_message('user').write(prompt)
    
    # LLM 모델을 사용하여 응답을 생성한다.
    response = client.chat.completions.create(
        model='gemma2-9b-it',
        messages=context + st.session_state['messages']  # context와 대화 기록을 결합하여 모델에 전달한다.
    )

    # 모델의 응답을 대화 기록에 추가하고 화면에 출력한다.
    msg = response.choices[0].message.content  # 모델의 응답 메시지 내용을 추출한다.
    st.session_state['messages'].append({'role': 'assistant', 'content': msg})
    st.chat_message('assistant').write(msg)   # 화면에 모델의 응답을 출력한다.

    # --- Comet Opik에 기록 ----------------------------------------------------
    utils.opik_trace(prompt, msg, context)
    # ------------------------------------------------------------------------
