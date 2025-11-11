import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import AffiliateLink, Click

app = FastAPI(title="Affiliate Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Affiliate Assistant Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ---------------- Affiliate Assistant Endpoints ----------------

@app.post("/api/links", response_model=dict)
async def create_link(link: AffiliateLink):
    # Ensure code is unique
    existing = db["affiliatelink"].find_one({"code": link.code}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Code already exists. Use another code.")
    inserted_id = create_document("affiliatelink", link)
    return {"id": inserted_id}

@app.get("/api/links", response_model=List[dict])
async def list_links(tag: Optional[str] = None):
    filter_dict = {"tags": {"$in": [tag]}} if tag else {}
    docs = get_documents("affiliatelink", filter_dict)
    # Convert ObjectId to string
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

@app.get("/api/stats", response_model=dict)
async def stats():
    total_links = db["affiliatelink"].count_documents({}) if db else 0
    total_clicks = db["click"].count_documents({}) if db else 0
    return {"total_links": total_links, "total_clicks": total_clicks}

@app.get("/r/{code}")
async def redirect(code: str, request: Request, source: Optional[str] = None):
    # Find target link
    doc = db["affiliatelink"].find_one({"code": code}) if db else None
    if not doc:
        raise HTTPException(status_code=404, detail="Link not found")
    # Log click
    click = Click(
        link_code=code,
        source=source,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    create_document("click", click)
    # Redirect to destination
    return RedirectResponse(url=doc.get("url"))

# ---------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
