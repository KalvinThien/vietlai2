import openai
import nltk
import random
import re
from nltk.tokenize import sent_tokenize, word_tokenize
import streamlit as st
from urllib.parse import urlparse

nltk.download('punkt')
st.title("Rewrite Contents")
st.markdown("By [Nguyễn Ngọc Thiện](https://techreviews.vn)")
st.markdown('---')
openai.api_key = st.text_input("Điền API Key Chatgpt -   [Lấy API KEY ChatGPT Ở Đây](https://platform.openai.com/account/api-keys) --- Nếu Chưa Có? [Mua Tài Khoản Có Sẵn 120$](https://zalo.me/0888884749)", type='password')
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

def insert_keywords_links(chunk, main_keyword, secondary_keywords, internal_url):
    secondary_keywords = secondary_keywords.split(',')
    urls = [url.strip() for url in internal_url.split(',') if url.strip() != ''] # Added condition to ignore empty URLs
    url_keywords = []

    for url in urls:
        path = urlparse(url).path
        path_keywords = path.strip('/').replace('-', ' ')
        url_keywords.append((path_keywords, url))

    for keyword, url in url_keywords:
        if keyword in chunk and chunk.count(url) < 1:
            chunk = chunk.replace(keyword, f"<a href='{url}'>{keyword}</a>", 1)
            
    for keyword in secondary_keywords:
        if keyword in chunk and urls and chunk.count(urls[0]) < 1:
            chunk = chunk.replace(keyword, f"<a href='{urls[0]}'>{keyword}</a>", 1)


    return chunk
def title_with_number(title, main_keyword):
    number_list = list(range(1,100))
    random.shuffle(number_list)
    number = number_list[0]
    new_title = f"{number} {title} {main_keyword}" # Added main_keyword
    if len(new_title) > 60:
        new_title = new_title[:60]
    return new_title


styles = ['Creative', 'Formal', 'Informal', 'Academic', 'Conversational', 'Persuasive', 'Descriptive', 'Instructional', 'Amazon Review', 'Amazon Guide']
selected_style = st.selectbox('Chọn Kiểu Viết', styles)
selected_style = selected_style.lower().replace(" ", "_")

def generate_rewritten_chunks(content, main_keywords, secondary_keywords, internal_url, style):
    secondary_keywords = secondary_keywords.split(',')
    random.shuffle(secondary_keywords) # shuffle secondary keywords for randomness

    chunks = split_content(content)
    rewritten_chunks = []
    for i, chunk in enumerate(chunks):
        secondary_keyword = secondary_keywords[i % len(secondary_keywords)] # cycle through secondary keywords
        section_title = f"Section {i+1}: {secondary_keyword}"
        section_title = title_with_number(section_title, secondary_keyword)
        
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
                    {'role': 'user', 'content': f"Your task is to rewrite the entire text in better language and Rewrite The Paragraph In Your Own Words Rather Than Copying And Pasting From Other Sources. Consider perplexity and burstiness when creating content, ensures high levels of both without losing specificity or context. Use fully detailed paragraphs that engage the reader. Write In A Conversational Style As Written By A Human (Use An Informal Tone, Utilize Personal Pronouns, Keep It Simple , Engage The Reader, Use The Active Voice, Keep It Brief, Use Rhetorical Questions, and Incorporate Analogies And Metaphors). Use the primary keyword '{main_keywords}' under the H2 heading and the secondary keyword '{secondary_keywords}' as content for better writing. Write in Markdown format and try to stretch the content more than the original. this is important to Bold the Title and all headings of the article, and use appropriate headings for H tags.All output should be in {selected_language}:\n\n{chunk}"}]


        response = openai.ChatCompletion.create(model=MODEL, messages=messages, temperature=0.8, max_tokens=2048)
        output = response.choices[0].message["content"]

        # Comment out or remove the line below if you only want URLs at the end
        # output = insert_keywords_links(output, main_keywords, secondary_keywords, internal_url)
        if i == 0: # only replace the main keyword in the first chunk
            output = output.replace(main_keywords, f"{main_keywords}", 1)
        rewritten_chunks.append({section_title: output})
    return rewritten_chunks

def rewrite_content(content, main_keywords, secondary_keywords, internal_url, style):
    rewritten_chunks = generate_rewritten_chunks(content, main_keywords, secondary_keywords, internal_url, style)
    rewritten_content = " ".join([chunk[list(chunk.keys())[0]] for chunk in rewritten_chunks])

    # Generate SEO Meta Description
    seo_description = f"{rewritten_content[:155]}..." # Summary of the content, limited to around 160 characters

    # Add SEO Meta Description at the beginning
    rewritten_content = f"## {seo_description}\n\n{rewritten_content}"

    # Add internal URLs at the end of the content if they exist
    urls = [url.strip() for url in internal_url.split(',') if url.strip() != ''] # Added condition to ignore empty URLs
    if urls:
        rewritten_content += "\n\n"
        for url in urls:
            rewritten_content += f"<a href='{url}'>{urlparse(url).path.strip('/').replace('-', ' ')}</a>\n"
    
    return rewritten_content

def generate_faq(content):
    system_message = "You are an intelligent AI that can generate insightful Frequently Asked Questions and their corresponding answers based on the provided content "
    user_message = f"Generate 5 pairs of Frequently Asked Questions and their Answers based on the following content: \n\n{content} "

    messages = [{'role': 'system', 'content': system_message}, {'role': 'user', 'content': user_message}]
    response = openai.ChatCompletion.create(model=MODEL, messages=messages, temperature=0.8, max_tokens=1000) # Increase max_tokens to have room for answers

    faq_pairs = response.choices[0].message["content"].split('\n\n') # Split by two newline characters to separate questions and answers
    faq_list = []
    for faq_pair in faq_pairs:
        if faq_pair.strip() != '':
            faq_list.append(faq_pair.strip().split('\n')) # Split by one newline character to separate a question from its answer
    return faq_list[:5]  # Limit to


content = st.text_area('Điền Nội Dung Cần Viết Lại', '')
languages = ['Vietnamese', 'English', 'Lao', 'Thai', 'Filipino']
selected_language = st.selectbox('Chọn Ngôn Ngữ Viết Lại', languages)
main_keywords = st.text_input('Điền Từ Khoá Chính', '')
secondary_keywords = st.text_input('Từ khoá phụ , cách nhau dấu phẩy', '')
internal_url = st.text_input('Điền Link Internal, cách nhau bởi dấu phẩy ', '')
faq_option = st.checkbox('Tạo 5 câu hỏi thường gặp hay không?')

if st.button('Viết Lại'):
    rewritten_content = rewrite_content(content, main_keywords, secondary_keywords, internal_url, selected_style)

    # Generate FAQs if the option is selected
    if faq_option:
        faqs = generate_faq(rewritten_content)
        faq_section = "\n## FAQ \n"
        for i, faq_pair in enumerate(faqs):
            question, answer = faq_pair[0], faq_pair[1] if len(faq_pair) > 1 else 'loading....'
            faq_section += f"\n### {i+1}: {question}\n\n: {answer}\n"
        rewritten_content += faq_section

    st.write(rewritten_content)
