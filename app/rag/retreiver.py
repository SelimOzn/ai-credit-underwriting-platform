from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory="data/chroma_db", embedding_function=emb)


def search_policy(query: str, max_k: int=5, min_k: int=3, distance_threshold: float=0.5):
    docs_and_scores = db.similarity_search_with_score(query=query, k=max_k)
    filtered_docs = []
    all_docs = []
    for doc, score in docs_and_scores:
        if score <= distance_threshold:
            filtered_docs.append(doc.page_content)
            all_docs.append(doc.page_content)

    if len(filtered_docs) < min_k:
        return all_docs

    return filtered_docs
