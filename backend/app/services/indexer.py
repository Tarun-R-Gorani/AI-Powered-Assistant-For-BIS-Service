import os
import json
import re
from typing import List

from bs4 import BeautifulSoup
from langchain_core.documents import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


def clean_bis_description(raw_text: str) -> str:
    """Clean BIS descriptions and remove unnecessary HTML/noise."""
    if not raw_text:
        return ""

    cleaned = BeautifulSoup(
        raw_text,
        "html.parser"
    ).get_text(separator=" ")

    boilerplate_patterns = [
        r"In order to promote public education and public safety.*?(?=(Division Name|Section Name|Title|$))",
        r"Step Out From the Old to the New.*?Satyanarayan Gangaram Pitroda",
        r"12 Tables of Code",
        r"Designator of Legally Binding Document:.*",
        r"Title of Legally Binding Document:.*",
        r"Number of Amendments:.*",
    ]

    for pattern in boilerplate_patterns:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL
        )

    return re.sub(r"\s+", " ", cleaned).strip()


def load_bis_standards(filepath: str) -> List[Document]:
    """Load BIS standards from JSON."""

    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = (
        data
        if isinstance(data, list)
        else data.get("standards", [])
    )

    documents = []

    for item in items:

        std_num = (
            item.get("standard_number")
            or item.get("standard_code")
            or item.get("is_number")
            or "Unknown"
        )

        title = item.get("title", "")

        clean_desc = clean_bis_description(
            item.get("description", "")
        )

        sector = (
            item.get("sector")
            or item.get("category")
            or "General"
        )

        year = (
            item.get("year")
            or item.get("publication_year")
            or ""
        )

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
    """Load BIS certification schemes."""

    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = (
        data
        if isinstance(data, list)
        else data.get("schemes", [data])
    )

    documents = []

    for item in items:

        scheme_name = (
            item.get("scheme_name")
            or item.get("name")
            or "BIS Scheme"
        )

        applicability = (
            item.get("applicability")
            or item.get("scope")
            or ""
        )

        desc = item.get("description", "")

        steps = (
            item.get("steps")
            or item.get("process")
            or item.get("checklist")
            or []
        )

        if isinstance(steps, list):
            steps_fmt = "\n".join(
                [f"- {step}" for step in steps]
            )
        else:
            steps_fmt = str(steps)

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
    """Load BIS FAQs."""

    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = (
        data
        if isinstance(data, list)
        else data.get("faqs", [])
    )

    documents = []

    for item in items:

        question = (
            item.get("question")
            or item.get("q")
            or ""
        )

        answer = (
            item.get("answer")
            or item.get("a")
            or ""
        )

        category = item.get(
            "category",
            "General"
        )

        content = (
            f"Question: {question}\n"
            f"Answer: {answer}"
        )

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source_file": "faqs.json",
                    "doc_type": "faq",
                    "category": category,
                },
            )
        )

    return documents


def load_all_documents() -> List[Document]:
    """Load all BIS knowledge-base documents."""

    docs = []

    docs.extend(
        load_bis_standards(
            os.path.join(
                settings.DATA_DIR,
                "bis_standards.json"
            )
        )
    )

    docs.extend(
        load_certification_schemes(
            os.path.join(
                settings.DATA_DIR,
                "certification_info.json"
            )
        )
    )

    docs.extend(
        load_faqs(
            os.path.join(
                settings.DATA_DIR,
                "faqs.json"
            )
        )
    )

    if not docs:
        docs.append(
            Document(
                page_content=(
                    "Bureau of Indian Standards "
                    "knowledge base placeholder."
                ),
                metadata={
                    "doc_type": "init"
                },
            )
        )

    return docs


class LightweightRetriever:
    """
    Lightweight TF-IDF based retriever.

    This avoids loading:
    - PyTorch
    - Sentence Transformers
    - HuggingFace embedding models

    This significantly reduces RAM usage during deployment.
    """

    def __init__(self, documents: List[Document]):

        self.documents = documents

        texts = [
            document.page_content
            for document in documents
        ]

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=12000
        )

        self.matrix = self.vectorizer.fit_transform(
            texts
        )

    def invoke(self, query: str) -> List[Document]:

        if not query.strip():
            return []

        if not self.documents:
            return []

        query_vector = self.vectorizer.transform(
            [query]
        )

        scores = cosine_similarity(
            query_vector,
            self.matrix
        )[0]

        top_indices = scores.argsort()[::-1][:4]

        return [
            self.documents[index]
            for index in top_indices
            if scores[index] > 0
        ]

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 3
    ):

        if not query.strip():
            return []

        query_vector = self.vectorizer.transform(
            [query]
        )

        scores = cosine_similarity(
            query_vector,
            self.matrix
        )[0]

        top_indices = scores.argsort()[::-1][:k]

        results = []

        for index in top_indices:

            distance = 1 - float(
                scores[index]
            )

            results.append(
                (
                    self.documents[index],
                    distance
                )
            )

        return results


def build_vector_store():
    """
    Build lightweight BIS retrieval system.
    """

    documents = load_all_documents()

    return LightweightRetriever(documents)


def get_vector_store():
    """
    Load BIS knowledge base.

    No FAISS or HuggingFace model is loaded.
    """

    return build_vector_store()