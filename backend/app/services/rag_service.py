from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.services.indexer import get_vector_store
from app.models.schemas import Citation, QueryResponse

class RAGService:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        self.llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name=settings.LLM_MODEL, temperature=0.1)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the BIS Smart Assistant. Answer concisely using ONLY the context.\nContext: {context}"),
            ("user", "{question}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def process_query(self, user_query: str) -> QueryResponse:
        docs = self.retriever.invoke(user_query)
        context_str = "\n\n---\n\n".join([d.page_content for d in docs])
        answer = self.chain.invoke({"context": context_str, "question": user_query})
        
        citations = [Citation(
            source_file=d.metadata.get("source_file", "unknown"),
            doc_type=d.metadata.get("doc_type", "general"),
            standard_id=d.metadata.get("standard_id"),
            title=d.metadata.get("title"),
            scheme=d.metadata.get("scheme")
        ) for d in docs]
            
        return QueryResponse(answer=answer, citations=citations, retrieved_context_count=len(docs))

    def find_standards_for_product(self, product: str, top_k: int = 3, distance_threshold: float = 1.2):
        # Returns a tuple of (Document, score) where a lower score is better
        results = self.vector_store.similarity_search_with_score(product, k=top_k)
        
        mapped = []
        for doc, score in results:
            # Only append if it's a standard AND the distance is below our strict threshold
            if doc.metadata.get("doc_type") == "standard" and score <= distance_threshold:
                mapped.append({
                    "standard_id": doc.metadata.get("standard_id"),
                    "title": doc.metadata.get("title"),
                    "details": doc.page_content,
                    "distance_score": round(float(score), 4) # Added so you can debug the threshold
                })
        return mapped
rag_service = RAGService()