# Preview
![image](https://github.com/jpotw/summarize_chattingroom/assets/105954991/9ed1e9b1-6072-4abc-8186-de108dab3c10)


# 핵심 기능 소개
1. 파일 자르기 기능(하루 전 내용까지만 자르기 가능)
2. URL만 추출 기능(제곧내)
3. 핵심 요약을 위한 프롬프트 템플릿
4. URL에 대한 설명을 위한 프롬프트 템플릿


# 사용 방법
1. 요약하고 싶은 카카오톡 방을 '카카오톡 내보내기'를 통해 txt파일로 저장해준다.
2. 업로드한다.
3. 잘린 파일을 다운로드한다.
4. URL, 프롬프트 버튼을 누른다.
5. 프롬프트를 복사한 후 첨부한 링크(claude.ai)로 간다.
6. 프롬프트 붙여넣고 잘린 파일을 업로드한다.
7. 계속 채팅하면 된다.

# Requirements(로컬에서 돌릴 경우)

```
pip install streamlit
pip install streamlit-scrollable-textbox
```

# 귀찮을 경우
streamlit 서버에 올려놔서 이 링크 타고 들어가도 됩니다
https://summarizechattingroom-final.streamlit.app/
