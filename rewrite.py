import streamlit as st
import openai
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download('punkt')

# Set up OpenAI API
openai.api_key = "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"

# Function to count tokens (approximate)
def count_tokens(text):
    return len(word_tokenize(text))

# Title of the app
st.title('Rewriting App - By Thiện')

# Form for content
content = st.text_area('Điền Nội Dung Cần Viết Lại', '')

# Select language
languages = ['Vietnamese', 'English', 'Lao', 'Thai', 'Filipino']
selected_language = st.selectbox('Chọn Ngôn Ngữ Viết Lại', languages)

# Enter main and secondary keywords
main_keywords = st.text_input('Điền Từ Khoá Chính', '')
secondary_keywords = st.text_input('Từ khoá phụ , cách nhau dấu phẩy', '')

# Select pronoun
pronouns = ['Tôi', 'Chúng Tôi']
selected_pronoun = st.selectbox('Chọn Cách Xưng Hô', pronouns)

# Enter internal URL
internal_url = st.text_input('Điền Link Internal, cách nhau bởi dấu phẩy ', '')

# Replace main keywords with H2 tags and secondary keywords with H3 tags
for keyword in main_keywords.split(','):
    content = content.replace(keyword, f"<h2>{keyword}</h2>")

for keyword in secondary_keywords.split(','):
    content = content.replace(keyword, f"<h3>{keyword}</h3>")

# Replace relevant words with internal URLs
for url in internal_url.split(','):
    keyword = url.split('/')[-1]  # Assume the last part of the URL is the relevant keyword
    content = content.replace(keyword, f"<a href='{url}'>{keyword}</a>")

# Button for rewriting
if st.button('Viết Lại'):
    # Split the content into sentences
    sentences = sent_tokenize(content)
    chunks = []
    chunk = ""
    word_count = 0
    for sentence in sentences:
        word_count += count_tokens(sentence)
        if word_count <= 800:
            chunk += ' ' + sentence
        else:
            chunks.append(chunk)
            chunk = sentence
            word_count = count_tokens(sentence)
    # Don't forget to add the last chunk
    if chunk:
        chunks.append(chunk)

    for chunk in chunks:
        # Use the OpenAI API to rewrite the chunk
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Viết lại đoạn văn bản sau bằng cách sử dụng từ khóa chính {main_keywords} trong thẻ H2 và từ khóa phụ {secondary_keywords} trong thẻ H3. Sử dụng danh xưng {selected_pronoun}. viết theo định dạng Markdown . Cố gắng viết dài hơn "},
            {"role": "user", "content": chunk}
        ],
        temperature=0.7
    )

        rewritten_chunk = response['choices'][0]['message']['content']
        st.write(rewritten_chunk)
