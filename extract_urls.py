import re

def extract_urls(input_file):

    # Define the regex pattern for URLs
    pattern = r'https://[^\s,]+'
    
    # Find all matches using the regex
    urls = re.findall(pattern, input_file)

    clickable_urls = '\n'.join([f"{index + 1}. [{url}]({url})" for index, url in enumerate(urls)])
    return clickable_urls