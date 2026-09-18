from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.services.indexer import get_vector_store
from app.models.schemas import Citation, QueryResponse


class RAGService:

    def __init__(self):

        # Lightweight BIS retrieval
        self.vector_store = get_vector_store()

        self.retriever = self.vector_store

        # Groq LLM
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.1
        )

        # Prompt for clear, grounded answers
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are the BIS Smart Assistant.

Answer the user's question using ONLY the provided BIS context.

Rules:
- Give a clear and concise answer.
- Use bullet points when explaining multiple facts.
- Mention BIS Standard numbers when available.
- Do not invent information.
- If the context does not contain enough information, clearly say so.
- Keep the answer easy to understand.

Context:
{context}
"""
            ),
            (
                "user",
                "{question}"
            )
        ])

        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )

    def process_query(
        self,
        user_query: str
    ) -> QueryResponse:

        # Retrieve relevant BIS documents
        docs = self.retriever.invoke(
            user_query
        )

        # Build context
        context_str = "\n\n---\n\n".join(
            [
                doc.page_content
                for doc in docs
            ]
        )

        # Generate grounded answer
        answer = self.chain.invoke({
            "context": context_str,
            "question": user_query
        })

        # Build citations
        citations = [
            Citation(
                source_file=doc.metadata.get(
                    "source_file",
                    "unknown"
                ),
                doc_type=doc.metadata.get(
                    "doc_type",
                    "general"
                ),
                standard_id=doc.metadata.get(
                    "standard_id"
                ),
                title=doc.metadata.get(
                    "title"
                ),
                scheme=doc.metadata.get(
                    "scheme"
                )
            )
            for doc in docs
        ]

        return QueryResponse(
            answer=answer,
            citations=citations,
            retrieved_context_count=len(docs)
        )

    def find_standards_for_product(
        self,
        product: str,
        top_k: int = 3,
        distance_threshold: float = 1.2
    ):

        results = (
            self.vector_store
            .similarity_search_with_score(
                product,
                k=top_k
            )
        )

        mapped = []

        for doc, score in results:

            if (
                doc.metadata.get(
                    "doc_type"
                ) == "standard"
                and score <= distance_threshold
            ):

                mapped.append({
                    "standard_id": doc.metadata.get(
                        "standard_id"
                    ),
                    "title": doc.metadata.get(
                        "title"
                    ),
                    "details": doc.page_content,
                    "distance_score": round(
                        float(score),
                        4
                    )
                })

        return mapped


# Create service
rag_service = RAGService()