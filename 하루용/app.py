from utils import make_documents, make_new_file, extract_urls, summarize, generate_response
import streamlit as st

# interface (Streamlit 이용)

# 제목
st.title("🗒️✂️오픈 채팅방의 하루치 내용을 요약해드립니다")

# 카카오톡 txt 파일 업로드 하는 곳
uploaded_file = st.file_uploader('카카오톡 txt파일을 업로드하세요.', type='txt')

# 파일 자르기 from utils import make_new_file
if uploaded_file is not None:
    # '파일 자르는 중입니다' spinner 계속 돌아서 if True 추가함.
    if True:
        with st.spinner('파일을 자르는 중입니다.'):
            new_file = make_new_file(uploaded_file)
            st.write("파일을 잘랐습니다.")
    #내용 다 들어있는 Document 미리 만들어두기
    texts = make_documents(new_file=new_file)
    # URL 추출하기 from utils import extract_urls
    if st.button('URL만 추출하기'):
        st.write(("URL 모음:"))
        clickable_urls = extract_urls(new_file)
        st.markdown(clickable_urls, unsafe_allow_html=True)
    # 핵심 인사이트 요약하기 from utils import make_document, summarize
    if st.button('요약하기'):
        with st.spinner('요약중입니다.'):
            st.write(summarize(texts))
else: 
    st.error("아직 업로드된 파일이 없습니다.")
#추가 질문 적기
query_text = st.text_input('질문:')

# Form input and query
result = []
with st.form('qatrain', clear_on_submit=True):
    submitted = st.form_submit_button('질문하기', disabled=not query_text)
    if submitted:
        with st.spinner('답변 준비중...'):
            response = generate_response(texts, query_text)
            result.append(response)

if len(result):
    st.info(response)

#     chattingroom = st.text_input('채팅방 이름', type='default')
#     content = st.text_input('채팅방의 주제를 적어주세요. ex. 주식', type='default')
#     # openai_api_key = st.text_input('OpenAI API Key', type='password')
#     submitted = st.form_submit_button('입력')
#     if submitted:
#         stx.scrollableTextbox(f"""
#     당신은 지금부터 대화 내용 정리의 전문가입니다.

#     이 파일은 "{chattingroom}"이라는 채팅방의 기록입니다.
#     해당 채팅방에서는 주로 "{content}"을 주제로 이야기합니다.
#     해당 txt 파일에서 최종적으로 가장 언급이 많았던 많았던 주제 5가지 bullet point로 제시합니다.
#     """
#         )


# 필요없는거
st.sidebar.title("About")

st.sidebar.info(
        "카카오톡 채팅방의 내용을 요약합니다."
    )