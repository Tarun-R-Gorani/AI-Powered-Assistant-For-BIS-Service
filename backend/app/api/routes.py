from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, ProductMappingRequest, ProductMappingResponse
from app.services.rag_service import rag_service
from app.services.indexer import build_vector_store

router = APIRouter()

@router.post("/chat", response_model=QueryResponse, response_model_exclude_none=True)
async def chat_endpoint(request: QueryRequest):
    try:
        return rag_service.process_query(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/standards/auto-map", response_model=ProductMappingResponse)
async def auto_map_standard(request: ProductMappingRequest):
    standards = rag_service.find_standards_for_product(f"{request.product_description} {request.hsn_code or ''}".strip())
    return ProductMappingResponse(product=request.product_description, suggested_standards=standards)

@router.post("/reindex")
async def reindex_data():
    try:
        build_vector_store()
        rag_service.vector_store = rag_service.retriever.vectorstore = build_vector_store()
        return {"status": "success", "message": "FAISS index rebuilt"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))