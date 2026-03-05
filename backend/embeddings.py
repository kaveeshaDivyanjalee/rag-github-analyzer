import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


def build_vector_store(documents: list[dict]) -> FAISS:
    """Chunk documents and build FAISS vector store using local HuggingFace embeddings."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    langchain_docs = []
    for doc in documents:
        chunks = splitter.split_text(doc["content"])
        for i, chunk in enumerate(chunks):
            langchain_docs.append(Document(
                page_content=chunk,
                metadata={
                    "source": doc["source"],
                    "extension": doc["extension"],
                    "chunk": i,
                }
            ))

    if not langchain_docs:
        raise ValueError("No documents to index.")

    # Free local embeddings — no API key required
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    vector_store = FAISS.from_documents(langchain_docs, embeddings)
    return vector_store