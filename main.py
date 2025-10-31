import validators,streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader

# stream aap
st.set_page_config(page_title="Langchain: Summarize Text from YT or website")
st.title("Langchain: Summarize Text from YT or website")
st.subheader('Summarize URl')


# get the groq API key and url (yt and website) to be summarized
with st.sidebar:
    groq_api_key=st.text_input("Groq Api key",value="",type='password')

llm=ChatGroq(model='llama-3.3-70b-versatile',groq_api_key=groq_api_key)

generic_url=st.text_input('URL',label_visibility='collapsed')

prompt="""
write a concise and short summary of the following specch,
Speech:{text}
"""
prompt=PromptTemplate(
    input_variables=['text'],
    template=prompt
)

if st.button("summarization the content from YT or website"):
    if not groq_api_key.strip() or not generic_url.strip():
        st.error("Please provide the information to get started")
    elif not validators.url(generic_url):
        st.error("Please enter a valid url.it can may be a YT video url or website url")
    else:
        try:
            with st.spinner("Waiting..."):
                if "youtube.com" in generic_url:
                    loader=YoutubeLoader.from_youtube_url(generic_url,add_video_info=True)
                else:
                    loader=UnstructuredURLLoader(urls=[generic_url],ssl_verify=True,
                                                 headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"})
                docs=loader.load()

                ## chain for summarization
                chain=load_summarize_chain(llm,chain_type='stuff',prompt=prompt)
                output_summary=chain.run(docs)

                st.success(output_summary)
        except Exception as e:
            st.exception(f"Exception:{e}")