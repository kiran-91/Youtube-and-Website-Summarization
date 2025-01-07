import validators
import os
from dotenv import load_dotenv 
import logging
import streamlit as st 
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader

st.set_page_config(page_title="Langchain", page_icon="🔗", layout="wide")
st.title("Summary from Youtube and website")
st.subheader("Enter a Youtube URL or a website URL to get a summary")


load_dotenv()
with st.sidebar:
    groq_api_key=st.text_input("Enter your Groq API Key", type="password")
   
logging.debug(f"Groq API Key: {groq_api_key}")

generic_url=st.text_input("Enter a Youtube URL or a website URL", label_visibility="collapsed")

llm=ChatGroq(api_key=groq_api_key, model="llama-3.3-70b-versatile")
prompt_template=""" 
Provide a summary of the following content in 300 words:
Content: {text}
"""
prompt=PromptTemplate(template=prompt_template, input_variables=["text"])


if st.button("Summarize this URL"):
    #validating all the inputs
    if not groq_api_key.strip() or not generic_url.strip():
        st.error("Please enter a valid Groq API Key or URL")
    elif not validators.url(generic_url):
        st.error("Please enter a valid URL")
    else:
        try:
            with st.spinner("Loading..."):
                #loading the summarization chain
                if "youtube.com" in generic_url:
                    loader = YoutubeLoader.from_youtube_url(generic_url, add_video_info=False)
                else:
                    loader = UnstructuredURLLoader(urls=[generic_url], ssl_verify=False, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.3"})
                
                docs=loader.load()
                
                # summary chain 
                chain=load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                output_summary=chain.run(docs) 
                
                st.success(output_summary)
                   
        except Exception as e:
            st.error(f"An error occurred: {e}")
            logging.error(f"Error: {e}")
            
            # incase there is a token limit error
            if " please reduce your message size and try again" in str(e).lower():
                st.warning("""
                           **Why this error occurs:**
                - The content from the YouTube video or website is too long and exceeds the token limit of the model.
                
                **What to do:**
                - Try uploading shorter videos or content.
                - For more advanced use cases, consider upgrading to an API key with a higher token limit and access to more powerful models.   
                """)
            