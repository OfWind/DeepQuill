from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv('agent.env')
model = ChatOpenAI(
    model = 'gpt-4o',
    api_key=os.getenv("OPENAI_API_KEY"),
)

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

embeddings_model = OpenAIEmbeddings(api_key=os.getenv("EMBEDDING_API_KEY"),
                                    base_url="https://openkey.cloud/v1",)