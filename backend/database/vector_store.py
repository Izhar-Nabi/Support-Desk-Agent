import json
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


def init_vector_store():
    from backend.config import settings
    db_path = settings.VECTOR_DB_PATH
    
    embeddings = OpenAIEmbeddings()
    
    if os.path.exists(db_path) and os.listdir(db_path):
        return Chroma(persist_directory=db_path, embedding_function=embeddings)

    with open("data/support_articles.json", "r") as f:
        articles = json.load(f)

    texts = [f"{a['title']}: {a['content']}" for a in articles]
    metadatas = [{"source": a["title"]} for a in articles]

    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=db_path
    )
    vectorstore.persist()
    print("Vector store created and persisted.")
    return vectorstore