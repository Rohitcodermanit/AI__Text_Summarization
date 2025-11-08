import os
import validators, streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.schema import Document
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
from yt_dlp import YoutubeDL
from groq import Groq 
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Langchain: Summarize")
st.title("Summarize YouTube Video or Website")
st.subheader("Enter a URL below:")

groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

generic_url = st.text_input("Enter YouTube or Website URL", label_visibility="collapsed")

prompt = PromptTemplate(
    input_variables=["text"],
    template="""
Write a clear and meaningful summary of the following:
{text}
"""
)

def extract_youtube_id(url):
    try:
        if "shorts" in url:
            return url.split("/shorts/")[1].split("?")[0]
        parsed = urlparse(url)
        if parsed.hostname == "youtu.be":
            return parsed.path[1:]
        if parsed.hostname in ("www.youtube.com", "youtube.com"):
            return parse_qs(parsed.query)["v"][0]
    except:
        return None

def get_youtube_transcript(video_id):
    try:
        text = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return " ".join([t["text"] for t in text])
    except:
        pass

    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        for t in transcripts:
            if t.is_generated:
                auto = t.fetch()
                return " ".join([x["text"] for x in auto])
    except:
        pass

    return None  # No transcript exists

def transcribe_audio_from_youtube(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "/mnt/data/audio.mp3",
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["web"]
            }
        }
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    client = Groq(api_key=groq_api_key)

    with open("/mnt/data/audio.mp3", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )
        return transcript.text
        
def get_website_text(url):
    try:
        loader = UnstructuredURLLoader(urls=[url], ssl_verify=True)
        docs = loader.load()
        if docs and docs[0].page_content.strip():
            return " ".join([d.page_content for d in docs])
    except:
        pass

    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return " ".join(soup.stripped_strings)

def summarize_text(text):
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    docs = [Document(page_content=text)] 
    return chain.run(docs)

if st.button("Summarize"):
    if not validators.url(generic_url):
        st.error("Please enter a valid URL.")
        st.stop()

    with st.spinner("Processing..."):
        try:
            if "youtube.com" in generic_url or "youtu.be" in generic_url or "shorts" in generic_url:
                video_id = extract_youtube_id(generic_url)
                text_data = get_youtube_transcript(video_id)

                if text_data is None:
                    st.info("No captions found. Using Whisper to transcribe audio… 🎙️")
                    text_data = transcribe_audio_from_youtube(generic_url)

            else:
                text_data = get_website_text(generic_url)

            summary = summarize_text(text_data)
            st.success(summary)

        except Exception as e:
            st.error(f"Error: {e}")

