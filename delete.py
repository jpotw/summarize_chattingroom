import datetime
import streamlit as st
import re

## txt파일 자르기 리턴값: 새로운 txt파일


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
        st.write("수정되었습니다.")
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

