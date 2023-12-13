from utils import make_new_file, extract_urls
import streamlit as st
import streamlit_scrollable_textbox as stx


##################################################################################################################################################
# 여기서부터는 인터페이스(streamlit)
## 타이틀
st.title("🗎 오픈 채팅방의 하루 내용을 요약해드립니다.")

if 'clickable_urls' not in st.session_state:
    st.session_state.clickable_urls = None

# 파일 업로드
uploaded_file = st.file_uploader('카카오톡 txt파일을 업로드하세요.', type='txt')

# 파일 자르기
if uploaded_file is not None:
    with st.spinner('파일을 자르는 중입니다.'):
        new_file = make_new_file(uploaded_file)
        st.write("파일을 잘랐습니다.")
        st.download_button(
            label="자른 파일 다운로드",
            data=new_file,
            key='download_button'
        )
        # URL 추출하기
        if st.button('URL만 추출하기'):
            if extract_urls(new_file):
                st.write("URL:")
                st.session_state.clickable_urls = extract_urls(new_file)
                st.markdown(st.session_state.clickable_urls, unsafe_allow_html=True)
            else: 
                st.warning("URL이 없습니다.")
            # st.write(("URL 모음:"))
            # for url in extracted_urls:
            #     st.write(url)
else:
    st.error("아직 업로드된 파일이 없습니다.")


st.title("프롬프트 만들기")

## 프롬프트 만들기
with st.form('프롬프트 만들기', clear_on_submit=True):
    chattingroom = st.text_input('채팅방 이름', type='default')
    content = st.text_input('채팅방의 주제를 적어주세요. ex. 주식', type='default')
    # openai_api_key = st.text_input('OpenAI API Key', type='password')
    submitted = st.form_submit_button('핵심 요약용 프롬프트')
    if submitted:
        stx.scrollableTextbox(f"""
    당신은 지금부터 대화 내용 정리의 전문가입니다.

    이 파일은 "{chattingroom}"이라는 채팅방의 기록입니다.
    해당 채팅방에서는 주로 "{content}"을 주제로 이야기합니다.
    형식은 다음과 같습니다.
    '''
    #핵심 인사이트:
    내용: 해당 txt 파일에서 최종적으로 가장 언급이 많았던 많았던 주제 5가지 bullet point로 제시합니다.
    '''
    """
        )


## URL
with st.form('프롬프트 만들기2', clear_on_submit=True):
    submitted = st.form_submit_button('URL 설명용 프롬프트')
    if submitted and st.session_state.clickable_urls:  # clickable_urls가 정의되었는지 확인
        stx.scrollableTextbox(f"""
            첨부한 문서 내용을 바탕으로 아래 링크들에 대한 설명을 "링크 : 내용설명" 의 형식으로 설명 해주세요:
                {st.session_state.clickable_urls}""")
    #URL만 추출하기 버튼 안 누른 경우 예외 처리 필요!



if st.button('AI 채팅으로 이동'):
    st.markdown('[claude.ai](https://claude.ai)')



# 없어도 되는거
st.sidebar.title("About")

st.sidebar.info(
        "카카오톡 내용 요약해드림"
    )