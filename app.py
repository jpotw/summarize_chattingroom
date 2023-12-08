import datetime
import os
from delete import make_new_file
import streamlit as st
from langchain.llms import openai
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from extract_urls import extract_urls
import streamlit_scrollable_textbox as stx


#API 키 세팅
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def generate_response(new_file, query_text):
        # Split document into chunks
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        texts = text_splitter.create_documents([new_file])  # Ensure it's a list

        # Check if texts is empty
        if not texts:
            raise ValueError("No texts were generated from the document.")
        # Select embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # Create a vectorstore from documents
        db = Chroma.from_documents(texts, embeddings)
        # Create retriever interface
        retriever = db.as_retriever()
        # Create QA chain
        qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(openai_api_key=openai_api_key), chain_type='stuff', retriever=retriever)
        return qa.run(query_text)


##################################################################################################################################################
# 여기서부터는 인터페이스(streamlit)
## 타이틀
st.title("🗎 오픈 채팅방의 하루치 내용을 요약해드립니다.")


uploaded_file = st.file_uploader('카카오톡 txt파일을 업로드하세요.', type='txt')

if uploaded_file is not None:
    with st.spinner('파일을 자르는 중입니다.'):
        new_file = make_new_file(uploaded_file)
        st.write("파일을 잘랐습니다.")
        if st.button('꿀통 추출하기'):
            clickable_urls = extract_urls(new_file)
            st.markdown(clickable_urls, unsafe_allow_html=True)
            # st.write(("URL 모음:"))
            # for url in extracted_urls:
            #     st.write(url)
else:
    st.error("아직 업로드된 파일이 없습니다.")


## 프롬프트 만들기
with st.form('프롬프트 만들기', clear_on_submit=True):
    chattingroom = st.text_input('채팅방 이름', type='default')
    content = st.text_input('채팅방의 주제를 적어주세요. ex. 주식', type='default')
    # openai_api_key = st.text_input('OpenAI API Key', type='password')
    submitted = st.form_submit_button('입력')
    if submitted:
        stx.scrollableTextbox(f"""

    이 파일은 "{chattingroom}"이라는 채팅방의 기록입니다.
    해당 채팅방에서는 주로 "{content}"을 주제로 이야기합니다.

    ---

    해당 txt 파일에서 가장 언급이 많았던 많았던 주제 5가지로 bullet으로 제시합니다."""
        )

# Query text
query_text = st.text_input('질문 입력하기', placeholder = 'Ex. 요약을 원할 경우, 아래 프롬프트를 복사, 붙여넣기 해주세요.', disabled=not uploaded_file)


# Form input and query
result = []
with st.form('추가질의', clear_on_submit=True):
    submitted = st.form_submit_button('입력', disabled=not(query_text))
    if submitted:
        with st.spinner('답변 준비중..'):
            response = generate_response(new_file, query_text)
            result.append(response)

if len(result):
    st.info(response)



# 없어도 되는거
st.sidebar.title("About")

st.sidebar.info(
        "카카오톡 내용 요약해드림"
    )