from utils import make_documents, make_new_file, extract_urls, summarize, generate_response, generate_db
import streamlit as st

# interface (Streamlit 이용)

# 제목 & 사이드바
st.title("🗒️✂️오픈 채팅방의 하루치 내용을 요약해드립니다")

st.sidebar.title("About")
with st.sidebar:
        openai_api_key = st.text_input('OpenAI API Key', type='password')
        if st.button("저장하기"):
            if openai_api_key is not None and openai_api_key.startswith('sk-'):
                st.write("저장되었습니다.")
    


# # 카카오톡 txt 파일 업로드 하는 곳
uploaded_file = st.file_uploader('카카오톡 txt파일을 업로드하세요.', type='txt')

if 'texts' not in st.session_state:
    st.session_state.texts = None

if uploaded_file is not None:
    # 뒤에서도 '파일 자르는 중입니다' spinner 계속 돌아서 if True 추가함.
    if True:
        # # 파일 자르기 from utils import make_new_file
        with st.spinner('파일을 자르는 중입니다.'):
            new_file = make_new_file(uploaded_file)
            st.write("파일을 잘랐습니다.")
    #내용 다 들어있는 Document 미리 만들어두기
        st.session_state.texts = make_documents(new_file)
    # URL 추출하기 from utils import extract_urls
    if st.button('URL만 추출하기'):
        clickable_urls = extract_urls(new_file)
        if clickable_urls is not None:
            st.write(("URL 모음:"))
            st.markdown(clickable_urls, unsafe_allow_html=True)
        else:
            st.write("해당 날짜에 언급된 URL이 없습니다.")


# 핵심 인사이트 요약하기 from utils import make_document, summarize
with st.form('요약', clear_on_submit=True):
    submitted = st.form_submit_button('요약하기', disabled=not openai_api_key)
    if submitted and openai_api_key is not None:
        with st.spinner('요약중입니다.'):
            summarization = summarize(st.session_state.texts, openai_api_key)
            st.write(summarization)
            del openai_api_key

#추가 질문 적기
query_text = st.text_input('추가 질문:')

#데이터베이스 만들기(중복X)
if st.session_state.texts is not None and openai_api_key is not None:
    db = generate_db(st.session_state.texts, openai_api_key)

# 답변 내용 저장
result=[]

with st.form('qatrain', clear_on_submit=True):
    submitted = st.form_submit_button('질문하기', disabled=not query_text)
    if submitted:
        with st.spinner('답변 준비중...'):
            response = generate_response(db, query_text, openai_api_key)
            result.append(response)
            del openai_api_key


# 요약도 result에 포함시키고 싶었는데 자꾸 에러 떠가지고 그냥 일단은 QA만 포함
if len(result):
    st.info(response)

