import openai
from nltk.tokenize import sent_tokenize, word_tokenize
import streamlit as st
import random

# Replace 'your-openai-api-key' with your actual OpenAI API key
openai.api_key = st.text_input("API Key")

MODEL = "gpt-3.5-turbo"

# Function to count tokens (approximate)
def count_tokens(text):
    return len(word_tokenize(text))

def split_content(content, max_tokens=1000):
    sentences = sent_tokenize(content)
    chunks = []
    chunk = ""
    word_count = 0
    for sentence in sentences:
        word_count += count_tokens(sentence)
        if word_count <= max_tokens:
            chunk += ' ' + sentence
        else:
            chunks.append(chunk)
            chunk = sentence
            word_count = count_tokens(sentence)
    # Don't forget to add the last chunk
    if chunk:
        chunks.append(chunk)
    return chunks

from urllib.parse import urlparse

def insert_keywords_links(chunk, main_keyword, secondary_keywords, internal_url):
    secondary_keywords = secondary_keywords.split(',')
    urls = [url.strip() for url in internal_url.split(',')]
    url_keywords = []

    for url in urls:
        path = urlparse(url).path  # Get path from URL
        path_keywords = path.strip('/').replace('-', ' ')  # Replace dashes with spaces
        url_keywords.append((path_keywords, url))

    for keyword, url in url_keywords:
        if keyword in chunk:
            chunk = chunk.replace(keyword, f"<a href='{url}'>{keyword}</a>", 1)
            
    for keyword in secondary_keywords:
        if keyword in chunk:
            chunk = chunk.replace(keyword, f"<a href='{urls[0]}'>{keyword}</a>", 2)

    return chunk

styles = ['Creative', 'Formal', 'Informal', 'Academic', 'Conversational', 'Persuasive', 'Descriptive', 'Instructional', 'Amazon Review', 'Amazon Guide']
selected_style = st.selectbox('Chọn Kiểu Viết', styles)

# Convert selected style to lowercase and replace spaces with underscores
selected_style = selected_style.lower().replace(" ", "_")

# Then, in your generate_rewritten_chunks function
def generate_rewritten_chunks(content, main_keywords, secondary_keywords, internal_url, style):
    chunks = split_content(content)
    rewritten_chunks = []
    for i, chunk in enumerate(chunks):
        section_title = f"Section {i+1}"

        if style == "creative":
            system_message = "You are an imaginative and creative writer."
        elif style == "formal":
            system_message = "You are a formal writer, providing structured and professional content."
        elif style == "informal":
            system_message = "You are an informal writer, providing relaxed and conversational content."
        elif style == "academic":
            system_message = "You are an academic writer, focusing on providing informative and scholarly content."
        elif style == "conversational":
            system_message = "You are a conversational writer, able to create engaging and interactive content."
        elif style == "persuasive":
            system_message = "You are a persuasive writer, skilled at convincing and influencing your readers."
        elif style == "descriptive":
            system_message = "You are a descriptive writer, able to paint vivid pictures with your words."
        elif style == "instructional":
            system_message = "You are an instructional writer, adept at providing clear and detailed guides."
        elif style == "amazon_review":
            system_message = "You are a seasoned reviewer who has written many Amazon product reviews."
        elif style == "amazon_guide":
            system_message = "You are an expert on Amazon, providing detailed and helpful guides on how to use its services."

        messages = [{'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': f"Please completely rewrite the following text, ensuring that the main ideas are retained. Use the primary keyword {main_keywords} in the H2 tag and the secondary keyword {secondary_keywords} in the H3 tag. Write in Markdown format, try to expand the content and use the {selected_language} language :\n\n{chunk}"}]
        response = openai.ChatCompletion.create(model=MODEL, messages=messages, temperature=0.8, max_tokens=2048)
        output = response.choices[0].message["content"]
        output = insert_keywords_links(output, main_keywords, secondary_keywords, internal_url)
        rewritten_chunks.append({section_title: output})
    return rewritten_chunks



def rewrite_content(content, main_keywords, secondary_keywords, internal_url, style):
    # Call generate_rewritten_chunks with the additional style parameter
    rewritten_chunks = generate_rewritten_chunks(content, main_keywords, secondary_keywords, internal_url, style)
    return " ".join([chunk[list(chunk.keys())[0]] for chunk in rewritten_chunks])

# Form for content
content = st.text_area('Điền Nội Dung Cần Viết Lại', '')

# Select language
languages = ['Vietnamese', 'English', 'Lao', 'Thai', 'Filipino']
selected_language = st.selectbox('Chọn Ngôn Ngữ Viết Lại', languages)

# Enter main and secondary keywords
main_keywords = st.text_input('Điền Từ Khoá Chính', '')
secondary_keywords = st.text_input('Từ khoá phụ , cách nhau dấu phẩy', '')


# Enter internal URL
internal_url = st.text_input('Điền Link Internal, cách nhau bởi dấu phẩy ', '')


if st.button('Viết Lại'):
    rewritten_content = rewrite_content(content, main_keywords, secondary_keywords, internal_url, selected_style)

    st.write(rewritten_content)
