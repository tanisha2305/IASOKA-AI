import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="IASOKA-AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SymptomInput(BaseModel):
    user_id: str
    symptom_text: str


@app.get("/")
def health_check():
    return {"status": "IASOKA-AI backend running"}


@app.post("/api/symptoms")
def submit_symptoms(payload: SymptomInput):
    result = supabase.table("symptom_reports").insert({
        "user_id": payload.user_id,
        "symptom_text": payload.symptom_text,
    }).execute()

    return {"report": result.data}


@app.get("/api/facilities")
def get_facilities(type: str = None):
    query = supabase.table("healthcare_facilities").select("*")

    if type:
        query = query.eq("type", type)

    result = query.execute()

    return {"facilities": result.data}
