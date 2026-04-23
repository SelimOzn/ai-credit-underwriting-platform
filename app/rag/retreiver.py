from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory="data/chroma_db", embedding_function=emb)


def search_policy(query: str, k:int=3):
    docs = db.similarity_search(query=query, k=k)
    return [d.page_content for d in docs]

