import os

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

# -------------------------
# Supabase connection
# -------------------------

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase environment variables are missing")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# -------------------------
# FastAPI
# -------------------------

app = FastAPI(title="IASOKA-AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Models
# -------------------------

class SymptomInput(BaseModel):
    symptom_text: str


class LoginInput(BaseModel):
    email: str
    password: str


class SignupInput(BaseModel):
    email: str
    password: str


# -------------------------
# Health check
# -------------------------

@app.get("/")
def health_check():
    return {
        "status": "IASOKA-AI backend running"
    }


# -------------------------
# SIGN UP
# -------------------------

@app.post("/api/auth/signup")
def signup(payload: SignupInput):

    try:
        result = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password
        })

        return {
            "message": "Signup successful",
            "user": result.user.model_dump() if result.user else None
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Signup failed"
        )


# -------------------------
# LOGIN
# -------------------------

@app.post("/api/auth/login")
def login(payload: LoginInput):

    try:
        result = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })

        return {
            "message": "Login successful",
            "access_token": (
                result.session.access_token
                if result.session else None
            ),
            "user": (
                result.user.model_dump()
                if result.user else None
            )
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


# -------------------------
# AUTHENTICATE USER
# -------------------------

def get_current_user(authorization: str):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]

    try:
        user_response = supabase.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        return user_response.user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# -------------------------
# SUBMIT SYMPTOMS
# -------------------------

@app.post("/api/symptoms")
def submit_symptoms(
    payload: SymptomInput,
    authorization: str = Header(default=None)
):

    user = get_current_user(authorization)

    try:
        result = supabase.table("symptom_reports").insert({
            "user_id": user.id,
            "symptom_text": payload.symptom_text,
        }).execute()

        return {
            "report": result.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# -------------------------
# HEALTHCARE FACILITIES
# -------------------------

@app.get("/api/facilities")
def get_facilities(type: str = None):

    query = supabase.table(
        "healthcare_facilities"
    ).select("*")

    if type:
        query = query.eq("type", type)

    result = query.execute()

    return {
        "facilities": result.data
    }
