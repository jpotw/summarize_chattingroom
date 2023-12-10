import re
import datetime
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


# txt파일 자르기 함수; input: 카카오톡 txt파일(type: UploadedFile), output: 하루치 txt 파일 (type: Str)
def make_new_file(uploaded_document):
    # 1. 파일을 읽어준다.
    file = uploaded_document.read().decode("utf-8", errors="ignore")
    # 2. 목표하는 날짜(현재로부터 하루 전)를 정의한다. 카카오톡 txt파일은 ~년 ~월 ~일로 구성되어 있음.
    current_date = datetime.datetime.now()
    target_date = current_date - datetime.timedelta(days=1)
    target_date_str = f"{target_date.year}년 {target_date.month}월 {target_date.day}일"
    # 3.1. 하루 전 내용이 있을 경우, 인덱싱을 통해 new_content에 저장한다.
    if target_date_str in file:
        st.write(f"{target_date_str}의 기록을 찾았습니다.")
        start_index = file.index(target_date_str)
        new_content = file[start_index:]
        #4. 오픈채팅방에 있는 불필요하게 반복되는 [x|x|x] [오후 x] 를 지워준다 (없을수도 있으니 케이스 구분)
        if  r'\[.*?\] \[\S+ \S+\] ':
            pattern = r'\[.*?\] \[\S+ \S+\] '
            cleaned_text = re.sub(pattern, '', new_content)
            return cleaned_text
        else:
            return new_content
    # 3.2. 하루 전 내용이 없을 경우, 내용이 나올때까지 하루씩 뒤로 미룬다.  
    else:
        st.write(f"{target_date_str}의 기록을 찾을 수 없습니다.")
        #내용이 생길 때까지 하루씩 뺀다.
        while target_date_str not in file:
            target_date -= datetime.timedelta(days=1)
            target_date_str = f"{target_date.year}년 {target_date.month}월 {target_date.day}일"
        #3.2.1. txt파일 내에 날짜가 하나라도 있는 경우
        if target_date_str:
            st.write(f"{target_date_str}의 기록을 찾았습니다.")
            start_index = file.index(target_date_str)
            new_content = file[start_index:]
            #4. 오픈채팅방에 있는 불필요하게 반복되는 [x|x|x] [오후 x] 를 지워준다 (없을수도 있으니 케이스 구분)
            if  r'\[.*?\] \[\S+ \S+\] ':
                pattern = r'\[.*?\] \[\S+ \S+\] '
                cleaned_text = re.sub(pattern, '', new_content)
                return cleaned_text
            else:
                return new_content
        #3.2.2. txt파일 내에 날짜가 없는 경우
        else:
             st.warning("🚨날짜를 찾을 수 없습니다. 다른 파일을 업로드해주세요.")
    
# url 추출 함수; input: 하루치 txt 파일(Str), output: Str
def extract_urls(input_file):
    pattern = r'https://[^\s,]+'
    urls = re.findall(pattern, input_file)
    clickable_urls = '\n'.join([f"{index + 1}. [{url}]({url})" for index, url in enumerate(urls)])
    return clickable_urls


# Document 생성 함수; input: 하루치 txt 파일(type: Str), output: Document(type: Document(langchain))
def make_documents(new_file):
        # Split document into chunks -> str으로 구성된 list 만듦 -> text_splitter 변수에 저장
        text_splitter = CharacterTextSplitter(
             separator="\n",
             chunk_size=1000, #1000으로 했는데 적당한지 모르겠음.
             chunk_overlap=20,
             length_function = len,
             is_separator_regex = False,
        )
        # Document[page_content, metadata]의 값을 texts에 저장함.
        texts = text_splitter.create_documents([new_file])
        # 디버깅 쳌
        if not texts:
            raise ValueError("텍스트가 만들어지지 않았습니다.")
        return texts


## 요약 함수 (맵리듀스 이용): input: Document(type: Document(langchain)), output: 핵심 인사이트(Str)
def summarize(Document, openai_api_key):
    template = """
    Don't say, just do:  
    '''
    해당 대화 내용의 핵심 내용을 요약해주세요.
    {text}
    '''
    """
    combine_template ="""{text}
    요약 내용을 바탕으로 다음의 형식으로 제시해주세요:
    # 요약
    내용: 각 템플릿의 문장
    ...
    """
    prompt = PromptTemplate(template=template, input_variables=["text"])
    template.format(text=Document)
    combine_prompt= PromptTemplate(template=combine_template, input_variables=["text"])
    chain = load_summarize_chain(llm=ChatOpenAI(openai_api_key=openai_api_key), 
                             map_prompt=prompt, 
                             combine_prompt=combine_prompt, 
                             chain_type='map_reduce', 
                             verbose=True)
    return chain.run(Document)



## QA Train 함수; input: Str, Str output: Str
def generate_response(texts, query_text, openai_api_key):
        embeddings=OpenAIEmbeddings(openai_api_key=openai_api_key)
        if not embeddings:
            raise ValueError("임베딩 생성 실패")
        # Create a vectorstore from documents using OpenAI Embeddings
        db = Chroma.from_documents(texts, embeddings)
        if not db:
            raise ValueError("db 생성 실패")
        # Create retriever interface
        retriever = db.as_retriever()
        # Create QA chain chain type stuff 일단 생략
        qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(openai_api_key=openai_api_key, model_name='gpt-3.5-turbo'), retriever=retriever)
        if not qa:
            raise ValueError("QA Train 생성 실패")
        return qa.run(query_text)