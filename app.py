import datetime
import streamlit as st



# Calculate the target date as one week ago from the current date
current_date = datetime.datetime.now()
target_date = current_date - datetime.timedelta(days=7)


# Convert the target date to a string in the desired format
target_date_str = target_date.strftime("%Y-%m-%d")  # Modify the format as needed


# Read the content of the file
def read_file_content(file_path):
    with open(file_path, "rb") as file:
        content = file.read().decode("utf-8", errors="ignore")
    return content


# Search for the target date in the content
def search_target_date(content):
    found = False
    global target_date
    while not found and target_date >= current_date - datetime.timedelta(days=7):
        target_date_str = target_date.strftime("%Y년 %m월 %d일")  # Modify the format as needed
        if target_date_str in content:
            found = True
        else:
            target_date -= datetime.timedelta(days=1)
    return found, target_date_str


# If a matching date is found, remove content above that date
def remove_content_above_date(found, target_date_str, content):
    if found:
        start_index = content.index(target_date_str)
        new_content = content[start_index:]
        return new_content
    else:
        return None


# Drag and drop file input using Streamlit
st.title("채팅기록의 일주일치를 요약해드립니다.")

uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

if uploaded_file is not None:
    file_contents = uploaded_file.read().decode("utf-8", errors="ignore")
    found, target_date_str = search_target_date(file_contents)

    if found:
        new_content = remove_content_above_date(found, target_date_str, file_contents)
        if new_content is not None:
            st.success("Revised file generated.")
            # Create a download button for the revised file
            revised_file_name = "revised_text_file.txt"
            download_button = st.download_button(
                label="Download Revised File",
                data=new_content.encode("utf-8"),
                file_name=revised_file_name,
                mime="text/plain"
            )
            if download_button:
                st.write("File downloaded successfully.")
        else:
            st.warning("No matching date found in the past week.")
    else:
        st.warning("No matching date found in the past week.")
else:
    st.warning("No file selected.")

# Additional layout/design elements for a search engine-like feel
st.sidebar.title("About")
st.sidebar.info(
    "txt 파일의 핵심 인사이트를 요약해드립니다."
)


prompt = """
    당신은 지금부터 대화 내용 정리의 전문가입니다. 
    이 파일은 {채팅방 이름}이라는 채팅방의 기록입니다.
    해당 채팅방에서는 주로 {내용}을 주제로 이야기합니다.
    해당 txt 파일을 다음의 형식으로 정리해서 보여주세요:
    ---
    # 주요 인사이트/통찰점 
    관련해서 가장 많은 언급/반응이 있었던 내용을 기준으로 합니다.
    # 언급되었던 URL 모음 
    {링크} - {링크에 대한 설명} 형식으로 적어주세요. 
    --- 
    사용자가 추가 질문이 있다면 txt 파일 내의 지식을 이용하여 답변해주세요.
    """
st.text_area("프롬프트(Ctrl C+V로 복사)", value=prompt, height=300)


url = "https://claude.ai/"


if st.button("채팅창으로 가기"):
    st.markdown(f"[Claude AI]({url})")




###########################################################################
# #여기서부터 txt 분석 및 답변

# load_dotenv()


# #Prompt

# #채팅방 제목 specify 기능 추가하면 좋음

# txt_path = file_contents
# loader = UnstructuredMarkdownLoader(txt_path)

# prompt_template = PromptTemplate.from_template(
#     f"Don't say, just do:  
#     ''' 
#     당신은 지금부터 대화 내용 정리의 전문가입니다. 
#     해당 txt 파일을 다음의 형식으로 정리해서 보여주세요:  
#     ---  
#     # 주요_인사이트
#     가장 많은 언급/반응이 있었던 내용을 기준으로 합니다.
#     # 언급되었던_URL_모음
#     '링크: 링크에 대한 설명' 형식으로
#     * 사용자가 추가 질문이 있다면 txt 파일 내의 지식을 이용하여 답변해주세요."
# )
# prompt_template.format()





# # Function to load and process PDFs
# def load_and_process_pdfs(pdf_paths):
#     all_texts = []
#     for path in pdf_paths:
#         loader = PyPDFLoader(path)
#         pages = loader.load_and_split()
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=20, length_function=len, is_separator_regex=False)
#         texts = text_splitter.split_documents(pages)
#         all_texts.extend(texts)
#     return all_texts


# def embed_texts(texts):
#     embeddings_model = OpenAIEmbeddings()
#     db = Chroma.from_documents(texts, embeddings_model)
#     return db


# # Load, process, and embed PDFs
# processed_texts = load_and_process_pdfs(pdf_paths)
# embedded_db = embed_texts(processed_texts)