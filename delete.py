import datetime
import os

# Calculate the target date as one week ago from the current date
current_date = datetime.datetime.now()
target_date = current_date - datetime.timedelta(days=7)

desktop_dir = os.path.expanduser(r"C:\Users\parkj\OneDrive\바탕 화면")
file_name = "revised_text_file.txt"  # Specify the desired file name
file_path = os.path.join(desktop_dir, file_name)


# Convert the target date to a string in the desired format
target_date_str = target_date.strftime("%Y-%m-%d")  # Modify the format as needed

# Specify the path to your text file
source_file_path = r"C:\kakao_crawl\AI로 업무 자동화하기1.txt"

# Read the content of the file
with open(source_file_path, "rb") as file:
    content = file.read().decode("utf-8", errors="ignore")

found = False

# Search for the target date in the content
while not found and target_date >= current_date - datetime.timedelta(days=7):
    target_date_str = target_date.strftime("%Y년 %m월 %d일")  # Modify the format as needed
    if target_date_str in content:
        found = True
    else:
        target_date -= datetime.timedelta(days=1)

# If a matching date is found, remove content above that date
if found:
    start_index = content.index(target_date_str)
    new_content = content[start_index:]
    
    # Write the modified content back to the file in binary mode ('wb')
    with open(file_path, "wb") as file:
        file.write(new_content.encode("utf-8"))
    print("Revised file saved to the desktop.")
else:
    print("No matching date found in the past week.")