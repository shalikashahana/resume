import io
import json
import os
import re
from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

import pdfplumber
from google import genai
from google.genai import errors as genai_errors

from ats import calculate_ats_score
from prompts import build_gemini_prompt, get_fallback_response
from tts import generate_villain_audio

load_dotenv()

app = FastAPI(title="Resume Villain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

def extract_text_from_file(filename: str, contents: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    if ext == ".pdf":
        try:
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                extracted = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted.append(page_text)
                text = "\n".join(extracted).strip()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Unable to parse PDF. Please ensure the file is not corrupted."
            )
    elif ext in [".txt", ""]:
        try:
            text = contents.decode("utf-8").strip()
        except UnicodeDecodeError:
            try:
                text = contents.decode("latin-1", errors="ignore").strip()
            except Exception:
                raise HTTPException(status_code=400, detail="Unable to read text file.")
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a PDF or .txt file."
        )

    if not text or len(text) < 30:
        raise HTTPException(
            status_code=400,
            detail="Empty or scanned PDF detected. Please upload a resume with selectable text."
        )

    return text

def parse_gemini_json(raw_text: str) -> Optional[dict]:
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    # Strip markdown code fences if present
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
    if match:
        cleaned = match.group(1).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        # Fallback regex search for json object
        json_obj = re.search(r'(\{[\s\S]*\})', cleaned)
        if json_obj:
            try:
                return json.loads(json_obj.group(1))
            except Exception:
                return None
        return None

@app.get("/")
def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Resume Villain backend is running. POST to /api/analyze"}

@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    language: str = Form("English"),
    villain_style: str = Form("chaotic"),
    level: str = Form("easy")
):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 2MB limit. Please upload a smaller file."
        )

    # Validate level
    valid_level = level.lower().strip() if level and level.lower().strip() in ["easy", "moderate", "hard"] else "easy"

    extracted_text = extract_text_from_file(file.filename or "resume.txt", contents)
    ats_result = calculate_ats_score(extracted_text)
    score = ats_result["score"]
    breakdown = ats_result["breakdown"]
    weak_points = ats_result["weak_points"]
    strong_points = ats_result["strong_points"]

    # Gemini Call
    api_key = os.getenv("GEMINI_API_KEY")
    villain_message = None
    real_tips = None

    if not api_key or api_key == "your_gemini_api_key_here":
        fallback = get_fallback_response(score, language, level=valid_level)
        villain_message = fallback["message"]
        real_tips = fallback["real_tip"]
    else:
        prompt = build_gemini_prompt(
            language=language,
            style_key=villain_style,
            score=score,
            breakdown=breakdown,
            weak_points=weak_points,
            strong_points=strong_points,
            resume_excerpt=extracted_text,
            level=valid_level
        )

        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            parsed = parse_gemini_json(response.text)
            if parsed and isinstance(parsed, dict) and "message" in parsed:
                villain_message = parsed["message"]
                tips = parsed.get("real_tip", [])
                if isinstance(tips, list):
                    real_tips = [str(t) for t in tips]
                else:
                    real_tips = [str(tips)]
            else:
                fallback = get_fallback_response(score, language, level=valid_level)
                villain_message = response.text[:600] if response.text else fallback["message"]
                real_tips = fallback["real_tip"]

        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
                fallback = get_fallback_response(score, language, level=valid_level)
                villain_message = "Rate limit reached. The villain is swamped with resumes! Please try again in a minute."
                real_tips = fallback["real_tip"]
            else:
                fallback = get_fallback_response(score, language, level=valid_level)
                villain_message = fallback["message"]
                real_tips = fallback["real_tip"]

    return {
        "score": score,
        "breakdown": breakdown,
        "weak_points": weak_points,
        "strong_points": strong_points,
        "message": villain_message,
        "real_tip": real_tips or [],
        "language": language,
        "villain_style": villain_style,
        "level": valid_level,
        "resume_text": extracted_text[:4000]  # for coach context
    }

class SpeakRequest(BaseModel):
    text: str
    language: str = "English"
    villain_style: str = "dramatic"
    level: str = "easy"


class CoachRequest(BaseModel):
    user_message: str
    resume_text: str = ""
    ats_score: int = 0
    weak_points: list = []
    strong_points: list = []
    villain_message: str = ""


@app.post("/api/coach")
async def coach(req: CoachRequest):
    if not req.user_message or not req.user_message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(status_code=503, detail="AI coach is unavailable (no API key).")

    system_prompt = (
        "You are an expert AI Resume Coach and Assistant integrated into the right-side chat panel of a 'Resume Roaster' web application.\n"
        "Your role is to assist the user in fixing the specific resume they just uploaded and roasted.\n\n"
        "Guidelines for your responses:\n"
        "1. TARGETED FEEDBACK: When the user asks for corrections or points to errors, clearly and concisely tell them what mistakes they made (e.g., grammatical errors, weak action verbs, lack of metrics).\n"
        "2. DIRECT CONTENT GENERATION: When the user asks for the corrected version (e.g., 'give me the correct version', 'fix my resume', 'generate text'), provide ONLY the updated, professionally polished, ATS-friendly resume content.\n"
        "3. COPY-PASTE READY: Format the final corrected content inside a clean markdown code block or plain text format so the user can easily copy and paste it directly into their resume template. Avoid unnecessary conversational filler when providing the final text block.\n"
        "4. TONE: Be helpful, sharp, professional, and encouraging."
    )

    context = f"""RESUME TEXT (what the user uploaded):
---
{req.resume_text[:3000] if req.resume_text else "(not provided)"}
---

ATS SCORE: {req.ats_score}/100
WEAK POINTS: {", ".join(req.weak_points) if req.weak_points else "none listed"}
STRONG POINTS: {", ".join(req.strong_points) if req.strong_points else "none listed"}
VILLAIN'S VERDICT: {req.villain_message[:400] if req.villain_message else "(not provided)"}

USER ASKS: {req.user_message.strip()}"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {"role": "user", "parts": [{"text": system_prompt + "\n\n" + context}]}
            ]
        )
        return {"reply": response.text.strip()}
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
            raise HTTPException(status_code=429, detail="Coach is resting, try again in a minute.")
        raise HTTPException(status_code=500, detail="Coach is unavailable right now. Please try again.")

@app.post("/api/speak")
def speak(req: SpeakRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        wav_audio = generate_villain_audio(
            text=req.text,
            language=req.language,
            villain_style=req.villain_style,
            level=req.level
        )
        return Response(content=wav_audio, media_type="audio/wav")
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
            raise HTTPException(status_code=429, detail="Voice is resting, try again in a minute")
        raise HTTPException(status_code=500, detail="Voice is resting, try again in a minute")


