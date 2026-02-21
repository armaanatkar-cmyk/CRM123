from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SearchRequest, SearchResponse
from services import run_search_logic

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    try:
        # DDGS is synchronous, so we could wrap this in run_in_executor if needed for high load
        # For now, simplistic approach
        results = run_search_logic(request.query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "ok", "service": "ICP Finder Backend"}
