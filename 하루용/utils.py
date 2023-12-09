from langchain.llms import openai
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import re
import datetime
import streamlit as st


## txt파일 자르기 함수; input: UploadedFile, output: Str
def make_new_file(uploaded_document):
    current_date = datetime.datetime.now()
    target_date = current_date - datetime.timedelta(days=1)
    file = uploaded_document.read().decode("utf-8", errors="ignore")

    target_date_str = f"{target_date.year}년 {target_date.month}월 {target_date.day}일"
    
    if target_date_str in file:
        st.write(f"{target_date_str}의 기록을 찾았습니다.")
        start_index = file.index(target_date_str)
        new_content = file[start_index:]
        # Regular expression pattern to match the parts you want to remove
    # Adjust the pattern as necessary based on the exact format
        pattern = r'\[.*?\] \[\S+ \S+\] '
    # Replace the matched patterns with an empty string
        cleaned_text = re.sub(pattern, '', new_content)
        # st.write("수정되었습니다.")
        return cleaned_text
        
    else:
        st.write(f"{target_date_str}의 기록을 찾을 수 없습니다.")
        while target_date_str not in file:
            target_date_str -= datetime.timedelta(days=1)
        st.write(f"{target_date_str}의 기록을 찾았습니다.")
        start_index = file.index(target_date_str)
        new_content = file[start_index:]
        pattern = r'\[.*?\] \[\S+ \S+\] '
    
    # Replace the matched patterns with an empty string
        cleaned_text = re.sub(pattern, '', new_content)

        st.write("수정되었습니다.")
        return cleaned_text
    
## url 추출 함수; input: Str, output: Str
def extract_urls(input_file):

    # Define the regex pattern for URLs
    pattern = r'https://[^\s,]+'
    
    # Find all matches using the regex
    urls = re.findall(pattern, input_file)

    clickable_urls = '\n'.join([f"{index + 1}. [{url}]({url})" for index, url in enumerate(urls)])
    return clickable_urls


#API 키 세팅
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
llm= ChatOpenAI(temperature=0, openai_api_key=openai_api_key)

## Document 생성 함수; input: Str, output: Document
def make_documents(new_file):
        # Split document into chunks -> str으로 구성된 list 만듦 -> text_splitter 변수에 저장
        text_splitter = CharacterTextSplitter(
             separator="\n",
             chunk_size=700, 
             chunk_overlap=20,
             length_function = len,
             is_separator_regex = False,
        )
        # Document[page_content, metadata]의 값을 texts에 저장함. 여기서 우리는 Document의 page content에 관심이 있는 것. page_content는 chunk들을 모아둔 list라 보면 됨.
        texts = text_splitter.create_documents([new_file])  # Ensure it's a list
        # Check if texts is empty
        if not texts:
            raise ValueError("No texts were generated from the document.")
        return texts


## 요약 함수: input: Document, output: Str
def summarize(Document):
    template = """
    Don't say, just do:  
    '''
    해당 대화 내용의 핵심 내용을 요약해주세요.
    {text}
    '''
    """
    combine_template ="""{text}
    요약의 결과를 다음과 같은 형식으로 적어주세요.:
    ---
    # 핵심 인사이트
    내용: 주요 내용을 불렛포인트 형식으로 작성
    ...
    """
    prompt = PromptTemplate(template=template, input_variables=["text"])
    template.format(text=Document)
    combine_prompt= PromptTemplate(template=combine_template, input_variables=["text"])
    chain = load_summarize_chain(llm=llm, 
                             map_prompt=prompt, 
                             combine_prompt=combine_prompt, 
                             chain_type='map_reduce', 
                             verbose=False)
    return chain.run(Document)



## QA Train 함수; input: Str, Str output: Str
def generate_response(texts, query_text):
        # Select embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        if not embeddings:
            raise ValueError("No embeddings generated")
        # Create a vectorstore from documents using OpenAI Embeddings
        db = Chroma.from_documents(texts, embeddings)
        # Create retriever interface
        retriever = db.as_retriever()
        # Create QA chain chain type stuff 일단 생략
        qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(openai_api_key=openai_api_key), retriever=retriever)
        if not qa:
            raise ValueError("No qa chain generated")
        return qa.run(query_text)