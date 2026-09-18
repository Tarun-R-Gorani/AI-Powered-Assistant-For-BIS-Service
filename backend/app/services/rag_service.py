from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.services.indexer import get_vector_store
from app.models.schemas import Citation, QueryResponse


class RAGService:

    def __init__(self):
        self.retriever = get_vector_store()

        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.1,
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are the BIS Smart Assistant.

Your job is to answer questions about Bureau of Indian Standards (BIS)
using ONLY the retrieved context provided below.

IMPORTANT RULES:

1. Do not invent information.
2. If the answer is not present in the context, clearly say:
   "I could not find this information in the available BIS knowledge base."
3. Give a direct answer first.
4. Make the answer easy to read.
5. Use Markdown formatting.
6. Use bullet points for multiple facts.
7. Use numbered steps when explaining a procedure.
8. Mention BIS Standard numbers whenever available.
9. Mention the standard title whenever available.
10. Keep the answer concise but useful.
11. Do not dump the entire retrieved document.
12. Do not repeat the question unnecessarily.

Preferred answer format:

**[Short descriptive heading]**

- **Standard:** IS XXXX
- **Title:** Standard title
- **Purpose:** Brief explanation
- **Key requirements:**
  - Requirement 1
  - Requirement 2
  - Requirement 3

If the question asks about a process:

**Process**

1. Step one
2. Step two
3. Step three

**Source**
- Mention the relevant BIS standard or scheme from the context.

Retrieved context:
{context}
"""
            ),
            ("user", "{question}"),
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    def process_query(self, user_query: str) -> QueryResponse:

        docs = self.retriever.invoke(user_query)

        if not docs:
            return QueryResponse(
                answer=(
                    "**No matching BIS information found**\n\n"
                    "- I could not find a relevant answer in the available "
                    "BIS knowledge base.\n"
                    "- Try using a BIS Standard number, product name, "
                    "certification scheme, or a more specific question."
                ),
                citations=[],
                retrieved_context_count=0,
            )

        context_str = "\n\n---\n\n".join(
            [doc.page_content for doc in docs]
        )

        answer = self.chain.invoke({
            "context": context_str,
            "question": user_query,
        })

        citations = [
            Citation(
                source_file=d.metadata.get(
                    "source_file",
                    "unknown"
                ),
                doc_type=d.metadata.get(
                    "doc_type",
                    "general"
                ),
                standard_id=d.metadata.get(
                    "standard_id"
                ),
                title=d.metadata.get(
                    "title"
                ),
                scheme=d.metadata.get(
                    "scheme"
                ),
            )
            for d in docs
        ]

        return QueryResponse(
            answer=answer,
            citations=citations,
            retrieved_context_count=len(docs),
        )

    def find_standards_for_product(
        self,
        product: str,
        top_k: int = 3,
        distance_threshold: float = 0.8,
    ):

        results = self.retriever.similarity_search_with_score(
            product,
            k=top_k,
        )

        mapped = []

        for doc, score in results:

            if (
                doc.metadata.get("doc_type") == "standard"
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
                    ),
                })

        return mapped


rag_service = RAGService()