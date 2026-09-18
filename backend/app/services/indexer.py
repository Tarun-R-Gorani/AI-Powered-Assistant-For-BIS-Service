import os
import json
import re
from typing import List
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings


def clean_bis_description(raw_text: str) -> str:
    """Strips HTML tags and removes common Archive.org legal boilerplate."""
    if not raw_text:
        return ""

    # Strip HTML tags
    cleaned = BeautifulSoup(raw_text, "html.parser").get_text(separator=" ")

    # Remove standard Archive.org legal disclaimers and metadata noise
    boilerplate_patterns = [
        r"In order to promote public education and public safety.*?(?=(Division Name|Section Name|Title|$))",
        r"Step Out From the Old to the New.*?Satyanarayan Gangaram Pitroda",
        r"12 Tables of Code",
        r"Designator of Legally Binding Document:.*",
        r"Title of Legally Binding Document:.*",
        r"Number of Amendments:.*",
    ]
    for pattern in boilerplate_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)

    # Normalize whitespace
    return re.sub(r"\s+", " ", cleaned).strip()


def load_bis_standards(filepath: str) -> List[Document]:
    """Loads and cleans Indian Standards data from JSON into searchable LangChain Documents."""
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data if isinstance(data, list) else data.get("standards", [])
    documents = []

    for item in items:
        std_num = (
            item.get("standard_number")
            or item.get("standard_code")
            or item.get("is_number")
            or "Unknown"
        )
        title = item.get("title", "")
        clean_desc = clean_bis_description(item.get("description", ""))
        sector = item.get("sector") or item.get("category") or "General"
        year = item.get("year") or item.get("publication_year") or ""

        # Emphasize standard code and product title for semantic retrieval
        content = (
            f"Standard Code: {std_num}\n"
            f"Product / Title: {title}\n"
            f"Sector / Domain: {sector}\n"
            f"Scope and Details: {clean_desc}\n"
            f"Publication Year: {year}"
        ).strip()

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source_file": "bis_standards.json",
                    "doc_type": "standard",
                    "standard_id": std_num,
                    "title": title,
                },
            )
        )
    return documents


def load_certification_schemes(filepath: str) -> List[Document]:
    """Loads certification workflows (ISI, CRS, Hallmarking) into searchable Documents."""
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data if isinstance(data, list) else data.get("schemes", [data])
    documents = []

    for item in items:
        scheme_name = item.get("scheme_name") or item.get("name") or "BIS Scheme"
        applicability = item.get("applicability") or item.get("scope") or ""
        desc = item.get("description", "")

        steps = item.get("steps") or item.get("process") or item.get("checklist") or []
        steps_fmt = (
            "\n".join([f"- {s}" for s in steps])
            if isinstance(steps, list)
            else str(steps)
        )

        content = (
            f"Scheme: {scheme_name}\n"
            f"Applicability: {applicability}\n"
            f"Overview: {desc}\n"
            f"Compliance Steps:\n{steps_fmt}"
        ).strip()

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source_file": "certification_info.json",
                    "doc_type": "certification_scheme",
                    "scheme": scheme_name,
                },
            )
        )
    return documents


def load_faqs(filepath: str) -> List[Document]:
    """Loads Q&A items for routine inquiries into Documents."""
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data if isinstance(data, list) else data.get("faqs", [])
    documents = []

    for item in items:
        q = item.get("question") or item.get("q") or ""
        a = item.get("answer") or item.get("a") or ""
        cat = item.get("category", "General")

        content = f"Question: {q}\nAnswer: {a}"
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source_file": "faqs.json",
                    "doc_type": "faq",
                    "category": cat,
                },
            )
        )
    return documents


def build_vector_store() -> FAISS:
    """Parses all 3 data files, generates embeddings, and saves a local FAISS index."""
    docs: List[Document] = []
    docs.extend(load_bis_standards(os.path.join(settings.DATA_DIR, "bis_standards.json")))
    docs.extend(load_certification_schemes(os.path.join(settings.DATA_DIR, "certification_info.json")))
    docs.extend(load_faqs(os.path.join(settings.DATA_DIR, "faqs.json")))

    if not docs:
        docs.append(
            Document(
                page_content="Bureau of Indian Standards knowledge base placeholder.",
                metadata={"doc_type": "init"},
            )
        )

    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(settings.FAISS_INDEX_PATH)
    return vector_store


def get_vector_store() -> FAISS:
    """Retrieves an existing FAISS index or builds one from scratch if missing."""
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)
    index_file = os.path.join(settings.FAISS_INDEX_PATH, "index.faiss")

    if os.path.exists(index_file):
        return FAISS.load_local(
            settings.FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return build_vector_store()