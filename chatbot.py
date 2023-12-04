from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import GooglePalmEmbeddings
from langchain.llms import GooglePalm
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import pinecone
import os
import time
import sys
import pyaudio
import gdown

import speech_recognition as sr
import win32com.client

speaker=win32com.client.Dispatch("SAPI.SpVoice")

folder_path=r"specify path in your system to store pdfs"

def download_file(url, folder_path,name):
    filename=os.path.basename(url)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    gdown.download(url,os.path.join(folder_path,name))



def say(text):
    speaker.Speak(text)

def takeCommand():
    r= sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold=0.6
        audio=r.listen(source)
        try:
            print("Recognizing...")
            query=r.recognize_google(audio,language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            return "Some error occurred"








if __name__ == '__main__':
    url=input("enter ur pdf link here")
    name=input("how would like to name the file (eg: filename.pdf)")
    download_file(url, folder_path, name)

    loader = PyPDFDirectoryLoader("pdfs")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks = text_splitter.split_documents(data)

    os.environ['GOOGLE_API_KEY'] = 'enter your google api key'
    embeddings = GooglePalmEmbeddings()
    #query_result = embeddings.embed_query("Hello World")


    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', 'enter your api key')
    PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV', 'gcp-starter')


    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_API_ENV
    )
    index_name = "pdf-chat"  # name of pinecone index

    docsearch = Pinecone.from_texts([t.page_content for t in text_chunks], embeddings, index_name=index_name)

    llm = GooglePalm(temperature=0.1)

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())
    prompt_template = """"""

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    say("Hello, how can i assist you")
    while (True):
        print("Listening...")
        query = takeCommand()

        if "stop".lower() in query.lower() or "shutdown".lower() in query.lower():
            say("Powering down")
            print("Goodbye...")
            time.sleep(2)
            exit(0)


        user_input = query
        result = qa({'query': user_input})
        say(result)
        print(f"Answer: {result['result']}")




