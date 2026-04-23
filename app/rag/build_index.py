from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

POLICY_PATH = Path("data/policies/lending_policy.txt")

def build_index():
    loader = TextLoader(POLICY_PATH)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)

    emb = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


    db = Chroma.from_documents(
        documents=chunks,
        embedding=emb,
        persist_directory="data/chroma_db"
    )

    print("Policy index created.")

if __name__ == "__main__":
    build_index()

