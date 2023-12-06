import datetime
import streamlit as st
from langchain.llms import openai
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


# 함수 정의

## txt파일 자르기 리턴값: 새로운 txt파일
def cut_and_search_target_date(content):
    current_date = datetime.datetime.now()
    target_date = current_date - datetime.timedelta(days=1)

    while target_date >= current_date - datetime.timedelta(days=30):  # 예를 들어, 최대 30일 전까지 검색
        target_date_str = target_date.strftime("%Y년 %m월 %d일")  # 날짜 형식은 파일에 맞춰 조정
        if target_date_str in content:
            start_index = content.index(target_date_str)
            return content[start_index:]
        target_date -= datetime.timedelta(days=1)

    return None  # 30일 내에 날짜를 찾지 못한 경우 None 반환


## new content를 벡터화하기

def new_content_data(content):
    if content is not None:
        # new_content 처리
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.create_documents(new_content)
        if texts:
            texts = text_splitter.create_documents(content)
            # Select embeddings
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            # Create a vectorstore from documents
            db = Chroma.from_documents(texts, embeddings)
        else:
            st.warning("처리할 텍스트가 없습니다.")
    else:
        st.warning("원하는 날짜의 데이터를 찾을 수 없습니다.")
    return db

## 자동답변
def first_reply(db):
    chattingroom=chattingroom
    content=content
    prompt = PromptTemplate(input_variables=["subject"],
    template=f"""
        당신은 지금부터 대화 내용 정리의 전문가입니다. 
        이 파일은 {chattingroom}이라는 채팅방의 기록입니다.
        해당 채팅방에서는 주로 {content}을 주제로 이야기합니다.
        해당 txt 파일을 다음의 형식으로 정리해서 보여주세요:
        ---
        # 주요 인사이트/통찰점 
        관련해서 가장 많은 언급이 많았던 주제 5가지를 bullet으로 제시합니다.
        # 언급되었던 URL 모음
        최소 5개의 링크를 제시합니다. 
        '링크' - '링크에 대한 설명' 형식으로 적어주세요. 
        --- 
        사용자가 추가 질문이 있다면 txt 파일 내의 지식을 이용하여 답변해주세요.
        """),
    return prompt.format(subject=db)
    


##추가질의용
def generate_response(db, query_text):
    # Create retriever interface
    retriever = db.as_retriever()
    # Create QA chain
    qa = RetrievalQA.from_chain_type(llm=openai(openai_api_key=openai_api_key), chain_type='stuff', retriever=retriever)
    return qa.run(query_text)   



# 여기서부터는 인터페이스(streamlit)
## 타이틀
st.title("🗎 오픈 채팅방의 하루치 내용을 요약해드립니다.")

## 업로드 파일
uploaded_file = st.file_uploader('카카오톡 txt파일을 업로드하세요.', type='txt')


## 채팅방 이름, 주제, API 키 입력칸
with st.form('폼1', clear_on_submit=True):
    chattingroom = st.text_input('채팅방 이름', type='default')
    content = st.text_input('채팅방의 주제를 적어주세요. ex. 주식', type='default')
    openai_api_key = st.text_input('OpenAI API Key', type='password')
    submitted = st.form_submit_button('입력')

    #입력했을 경우 1. txt파일 자르기 2. txt파일 벡터 db로 변환후 저장 3. 첫번째 답변
    if submitted and openai_api_key.startswith('sk-'):
        with st.spinner('채팅방의 핵심 인사이트를 요약하고 있습니다.'):
            if uploaded_file is not None:
                # 파일 내용 읽기
                file_contents = uploaded_file.read().decode("utf-8", errors="ignore")
                new_content = cut_and_search_target_date(file_contents)
                #일단 여기까진 성공... 근데 이 뒤부터 무한대기임 ㄷ
                db = new_content_data(new_content)
                print(first_reply(db))
                

# # Query text
# query_text = st.text_input('추가 질문하기:', placeholder = 'X에 대해 좀 더 자세히 알려줘', disabled=not uploaded_file)


# # Form input and query
# result = []
# with st.form('폼2', clear_on_submit=True):
#     submitted = st.form_submit_button('추가 질문하기', disabled=not(uploaded_file and query_text))
#     if submitted:
#         with st.spinner('질문중...'):
#             response = generate_response(db=db, query_text=query_text)
#             result.append(response)
#             del openai_api_key

# if len(result):
#     st.info(response)



# # 없어도 되는거
# st.sidebar.title("About")
# st.sidebar.info(
#     "오픈채팅방 핵심 내용만 요약해드립니다."
# )