import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS


ERROR_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert code reviewer and bug detector.
You have been given code from a GitHub repository. Analyze the provided code context carefully.

Context (code from repository):
{context}

Task: {question}

Your analysis should:
1. **Identify Bugs & Errors**: Syntax errors, logic errors, runtime errors, null pointer issues, off-by-one errors, etc.
2. **Security Vulnerabilities**: SQL injection, XSS, hardcoded secrets, insecure dependencies, etc.
3. **Code Quality Issues**: Dead code, unused variables, memory leaks, poor error handling, etc.
4. **Performance Issues**: Inefficient algorithms, N+1 queries, blocking calls, etc.
5. **Best Practice Violations**: Anti-patterns, missing type hints, no error handling, etc.

For each issue found, provide:
- 📁 **File**: the filename
- 🐛 **Issue Type**: (Bug / Security / Quality / Performance / Best Practice)
- 📝 **Description**: What the issue is
- 💡 **Fix Suggestion**: How to fix it

If no issues are found in the context, say so clearly.

Answer:"""
)


def format_docs(docs):
    """Format retrieved documents into a single string."""
    return "\n\n".join(
        f"### File: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    )


def build_rag_chain(vector_store: FAISS):
    """Build RAG chain using Groq (free) as the LLM."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=4096,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 8}
    )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | ERROR_ANALYSIS_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain, retriever


def analyze_errors(chain_and_retriever: tuple, query: str = None) -> dict:
    """Run error analysis on the repo."""
    chain, retriever = chain_and_retriever

    if query is None:
        query = (
            "Analyze ALL files in this repository thoroughly. "
            "Find every bug, error, security vulnerability, code quality issue, "
            "and best practice violation. Be specific about file names and line context."
        )

    answer = chain.invoke(query)
    source_docs = retriever.invoke(query)
    sources = list({doc.metadata["source"] for doc in source_docs})

    return {
        "answer": answer,
        "sources": sources
    }