import datetime
import os
from delete import make_new_file
import streamlit as st
from langchain.llms import openai
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv



#API 키 세팅
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


# 함수 정의
## new content를 벡터화해서 DB에 저장
def new_content_doc(new_file):
    if new_file is not None:
        # new_content 처리
        text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
        texts = text_splitter.create_documents(new_file)
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # Create a vectorstore from documents
        db = Chroma.from_documents(texts, embeddings)
    else:
        st.warning("데이터를 만들 수 없습니다.")
    return db


## 첫번째 대답 return: response based on prompt
def first_answer(chattingroom, content, db):
    # Create your custom prompt using the provided chattingroom and content
    custom_prompt = f"""
    당신은 지금부터 대화 내용 정리의 전문가입니다.

    {db}는 "{chattingroom}"이라는 채팅방의 기록입니다.

    해당 채팅방에서는 주로 "{content}"을 주제로 이야기합니다.

    해당 txt 파일을 다음의 형식으로 정리해서 보여주세요:

    ---

    # 주요 인사이트/통찰점

    관련해서 가장 많은 언급이 많았던 주제 5가지를 bullet으로 제시합니다.

    # 언급되었던 URL 모음

    최소 5개의 링크를 제시합니다.

    '링크' - '링크에 대한 설명' 형식으로 적어주세요.

    ---

    사용자가 추가 질문이 있다면 txt 파일 내의 지식을 이용하여 답변해주세요.
    """

    # Use LangChain's OpenAI interface to send the prompt
    response = openai(custom_prompt, temperature=0, api_key=openai_api_key)

    return response


##추가질의용
def generate_response(db, query_text):
    # Create retriever interface
    retriever = db.as_retriever()
    # Create QA chain
    qa = RetrievalQA.from_chain_type(llm=openai(openai_api_key=openai_api_key), chain_type='stuff', retriever=retriever)
    return qa.run(query_text)   

## 프롬프트에 대한 답변이요

def openai_response(prompt):
    openai.ChatCompletion.create(
                model="text-davinci-003",  # 모델을 지정하세요. 예: "text-davinci-003"
                prompt=prompt
                )

    # 생성된 텍스트 출력
    print(response.choices[0].text)


# 여기서부터는 인터페이스(streamlit)
## 타이틀
st.title("🗎 오픈 채팅방의 하루치 내용을 요약해드립니다.")


uploaded_file = st.file_uploader('카카오톡 txt파일을 업로드하세요.', type='txt')

if uploaded_file is not None:
    with st.spinner('파일을 자르는 중입니다.'):
        new_file = make_new_file(uploaded_file)
        st.write("파일을 잘랐습니다.")
else:
    st.error("아직 업로드된 파일이 없습니다.")


## 채팅방 이름, 주제, API 키 입력칸
with st.form('폼1', clear_on_submit=True):
    chattingroom = st.text_input('채팅방 이름', type='default')
    content = st.text_input('채팅방의 주제를 적어주세요. ex. 주식', type='default')
    # openai_api_key = st.text_input('OpenAI API Key', type='password')
    submitted = st.form_submit_button('입력')
    if submitted:
        new_content_doc(new_file)
        first_answer(chattingroom=chattingroom, content=content)


    result=[]
    result.append(first_answer)

                

# Query text
query_text = st.text_input('추가 질문하기:', placeholder = 'X에 대해 좀 더 자세히 알려줘', disabled=not uploaded_file)


# Form input and query
with st.form('폼2', clear_on_submit=True):
    submitted = st.form_submit_button('추가 질문하기', disabled=not(uploaded_file and query_text))
    if submitted:
        with st.spinner('질문중...'):
            response = generate_response(db=db, query_text=query_text)
            result.append(response)
            del openai_api_key

if len(result):
    st.info(response)



# 없어도 되는거
st.sidebar.title("About")

st.sidebar.info(
        "카카오톡 내용 요약해드림"
    )