import openai
import nltk
import random
import re
from nltk.tokenize import sent_tokenize, word_tokenize
import streamlit as st
from urllib.parse import urlparse

nltk.download('punkt')
st.title("Viết Lại Nội Dung")
st.markdown("By [Nguyễn Ngọc Thiện](https://techreviews.vn)")
st.markdown('---')
openai.api_key = st.text_input("Điền API Key Chatgpt - [Lấy API KEY ChatGPT Ở Đây](https://platform.openai.com/account/api-keys) --- Nếu Chưa Có? [Mua Tài Khoản Có Sẵn 120$](https://zalo.me/0888884749)", type='password')
MODEL = "gpt-3.5-turbo"

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
    if chunk:
        chunks.append(chunk)
    return chunks

def generate_rewritten_chunks(content, main_keywords, secondary_keywords, internal_url, style):
    secondary_keywords = secondary_keywords.split(',')
    random.shuffle(secondary_keywords) # shuffle secondary keywords for randomness

    chunks = split_content(content)
    rewritten_chunks = []

    for i, chunk in enumerate(chunks):
        secondary_keyword = secondary_keywords[i % len(secondary_keywords)] # cycle through secondary keywords
        section_title = f"## Section {i+1}: {secondary_keyword if i > 0 else main_keywords}" # ensure main keyword only appears in the first H2

        messages = [{'role': 'system', 'content': f"You are a {style} Your task is to rewrite the entire text in better language and Rewrite The Paragraph In Your Own Words Rather Than Copying And Pasting From Other Sources. Consider perplexity and burstiness when creating content, ensures high levels of both without losing specificity or context. Use fully detailed paragraphs that engage the reader. Write In A Conversational Style As Written By A Human (Use An Informal Tone, Utilize Personal Pronouns, Keep It Simple , Engage The Reader, Use The Active Voice, Keep It Brief, Use Rhetorical Questions, and Incorporate Analogies And Metaphors), incorporating the primary keyword '{main_keywords}' and the secondary keyword '{secondary_keyword}'.  this is important to Bold the Title and all headings of the article, and use appropriate headings for H tags. Write in a conversational style, demonstrate the content is easy, uses personal pronouns, is to read, brief and uses rhetorical questions. Ensure that the content is written in the Markdown format and try to make it longer than the original. Make sure to bold the title and all headings of the article, and use appropriate headings for H tags. The text to be rewritten is:\n\n{chunk}"}]
        response = openai.ChatCompletion.create(model=MODEL, messages=messages, temperature=0.8, max_tokens=2048)
        output = response.choices[0].message["content"]
        
        # Tạo tiêu đề dựa trên nội dung viết lại
        title_prompt = {'role': 'system', 'content': f"You are a {style}. Your task is to generate H2 and H3 titles based on the following content.Written By A Human (Use An Informal Tone, Utilize Personal Pronouns, Keep It Simple , Engage The Reader, Use The Active Voice, Keep It Brief, Use Rhetorical Questions, and Incorporate Analogies And Metaphors). Write in a conversational style, demonstrate the content is easy, uses personal pronouns, is to read, brief and uses rhetorical questions. Ensure that the content is written in the Markdown :\n\n{output}"}
        title_response = openai.ChatCompletion.create(model=MODEL, messages=[title_prompt], temperature=0.8, max_tokens=200)
        section_title = title_response.choices[0].message["content"]

        rewritten_chunks.append({section_title: output})
    return rewritten_chunks
def generate_title_and_seo(main_keywords, style):
    # Tạo prompt
    messages = [{'role': 'system', 'content': f"You are a {style}. Your task is to generate a H1 title and SEO Meta Description using the main keyword '{main_keywords}'. The title should be informative and engaging. The SEO Meta Description should describe the overall content of the article in a concise and appealing way."}]

    # Gọi ChatGPT
    response = openai.ChatCompletion.create(model=MODEL, messages=messages, temperature=0.8, max_tokens=120)

    # Lấy kết quả từ phản hồi của ChatGPT
    output = response.choices[0].message["content"].split('\n')

    # Tạo H1 title và SEO Meta Description
    h1_title = f"# {output[0]}\n" # H1 title
    seo_description = f"{output[1]}\n" # SEO Meta Description

    return h1_title, seo_description



def rewrite_content(content, main_keywords, secondary_keywords, internal_url, style):
    rewritten_chunks = generate_rewritten_chunks(content, main_keywords, secondary_keywords, internal_url, style)

    # Gọi hàm để tạo H1 title và SEO Meta Description
    h1_title, seo_description = generate_title_and_seo(main_keywords, style)

    # Chuỗi bắt đầu với H1 title và SEO Meta Description
    rewritten_content = h1_title + seo_description

    # Thêm các phần viết lại vào nội dung
    for chunk in rewritten_chunks:
        section_title = list(chunk.keys())[0]  
        section_content = chunk[section_title] + "\n"
        rewritten_content += section_title + "\n" + section_content

    return rewritten_content



content = st.text_area('Điền Nội Dung Cần Viết Lại', '')
languages = ['Vietnamese', 'English', 'Lao', 'Thai', 'Filipino']
selected_language = st.selectbox('Chọn Ngôn Ngữ Viết Lại', languages)
styles = ['Creative', 'Formal', 'Informal', 'Academic', 'Conversational', 'Persuasive', 'Descriptive', 'Instructional', 'Amazon Review', 'Amazon Guide']
selected_style = st.selectbox('Chọn Kiểu Viết', styles)
main_keywords = st.text_input('Điền Từ Khoá Chính', '')
secondary_keywords = st.text_input('Từ khoá phụ, cách nhau bằng dấu phẩy', '')
internal_url = st.text_input('Điền Link Internal, cách nhau bởi dấu phẩy', '')

if st.button('Viết Lại'):
    rewritten_content = rewrite_content(content, main_keywords, secondary_keywords, internal_url, selected_style.lower())
    st.markdown(rewritten_content)
