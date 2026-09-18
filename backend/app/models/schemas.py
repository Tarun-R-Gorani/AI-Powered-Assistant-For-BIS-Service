from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., example="What IS standard applies to gold jewellery hallmarking?")
    language: Optional[str] = Field("en", description="ISO language code, e.g., 'en', 'hi'")

class Citation(BaseModel):
    source_file: str
    doc_type: str
    standard_id: Optional[str] = None
    title: Optional[str] = None
    scheme: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    retrieved_context_count: int

class ProductMappingRequest(BaseModel):
    product_description: str
    hsn_code: Optional[str] = None

class ProductMappingResponse(BaseModel):
    product: str
    suggested_standards: List[Dict[str, Any]]