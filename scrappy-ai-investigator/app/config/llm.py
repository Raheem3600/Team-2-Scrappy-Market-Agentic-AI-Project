import os
#from langchain_openai import ChatOpenAI
#from dotenv import load_dotenv


#load_dotenv()


from langchain_community.chat_models import ChatOllama


def get_llm():
    return ChatOllama(
        model="llama3",
        temperature=0
    )