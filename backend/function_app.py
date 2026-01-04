import azure.functions as func
import datetime
import json
import logging
import hashlib
from datetime import timedelta

from cosmos_client import get_container
from openai import OpenAI

# =================================================
# AI CLIENT
# =================================================
client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

app = func.FunctionApp()

# =================================================
# RISK WORD LISTS
# =================================================
RISK_KEYWORDS = [
    "suicide", "kill myself", "end my life",
    "worthless", "hopeless", "give up",
    "self harm", "cut myself", "die"
]

HIGH_RISK_WORDS = [
    "suicide", "kill myself", "end my life"
]

# =================================================
# ENTER / REGISTER
# Users container partition key: /email
# =================================================
@app.route(route="enter", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def enter(req: func.HttpRequest):

    data = req.get_json()
    student_name = data.get("studentName")
    email = data.get("email")
    password = data.get("password")

    if not student_name or not email or not password:
        return func.HttpResponse(
            json.dumps({"error": "All fields are required"}),
            status_code=400
        )

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    users = get_container("users")
    users.upsert_item({
        "id": email,
        "email": email,
        "studentId": email,
        "studentName": student_name,
        "password": hashed_password,
        "createdAt": datetime.datetime.utcnow().isoformat()
    })

    return func.HttpResponse(json.dumps({"success": True}))

# =================================================
# CHAT (CALM FIRST AI)
# =================================================
@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest):

    data = req.get_json()
    message = data.get("message", "").strip()
    student_id = data.get("studentId")

    if not message:
        return func.HttpResponse(json.dumps({
            "reply": "I’m here 🤍 Take your time."
        }))

    # Short input override
    if message.lower() in ["hi", "hello", "hey", "what", "ok", "?"]:
        return func.HttpResponse(json.dumps({
            "reply": "Hi 🤍 I’m here with you. How are you feeling right now?"
        }))

    lower_msg = message.lower()

    matches = [w for w in RISK_KEYWORDS if w in lower_msg]
    risk_level = "HIGH" if any(w in lower_msg for w in HIGH_RISK_WORDS) else "MEDIUM" if len(matches) >= 2 else "LOW"
    risk_detected = len(matches) > 0

    SYSTEM_PROMPT = (
        "You are MindBridge, a calm and empathetic mental health companion for students. "
        "Speak gently and simply. Never sound like documentation. "
        "Use short supportive sentences. Validate feelings first."
    )

    response = client.chat.completions.create(
        model="tinyllama-1.1b-chat-v1.0",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0.25,
        top_p=0.85,
        max_tokens=120,
        frequency_penalty=0.9
    )

    reply = response.choices[0].message.content.strip()

    chats = get_container("chat_summaries")
    chats.create_item({
        "id": str(datetime.datetime.utcnow().timestamp()),
        "studentId": student_id,
        "userMessage": message,
        "botReply": reply,
        "riskDetected": risk_detected,
        "riskLevel": risk_level,
        "createdAt": datetime.datetime.utcnow().isoformat()
    })

    if risk_detected:
        alerts = get_container("risk_alerts")
        since = (datetime.datetime.utcnow() - timedelta(hours=24)).isoformat()

        recent = list(alerts.query_items(
            query="SELECT * FROM a WHERE a.studentId=@sid AND a.detectedAt>@t",
            parameters=[
                {"name": "@sid", "value": student_id},
                {"name": "@t", "value": since}
            ],
            enable_cross_partition_query=True
        ))

        if not recent:
            alerts.create_item({
                "id": str(datetime.datetime.utcnow().timestamp()),
                "studentId": student_id,
                "riskLevel": risk_level,
                "reason": "Distress detected in chat",
                "detectedAt": datetime.datetime.utcnow().isoformat(),
                "status": "NEW"
            })

    return func.HttpResponse(json.dumps({"reply": reply}))

# =================================================
# MOOD
# =================================================
@app.route(route="mood", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def mood(req: func.HttpRequest):

    data = req.get_json()
    student_id = data.get("studentId")
    mood = data.get("mood")

    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    moods = get_container("moods")
    moods.upsert_item({
        "id": f"{student_id}_{today}",
        "studentId": student_id,
        "mood": mood,
        "date": today,
        "createdAt": datetime.datetime.utcnow().isoformat()
    })

    return func.HttpResponse(json.dumps({"success": True}))

# =================================================
# COUNSELLOR ALERTS
# =================================================
@app.route(route="counsellor/alerts", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def counsellor_alerts(req: func.HttpRequest):

    alerts = get_container("risk_alerts")
    items = list(alerts.query_items(
        query="SELECT * FROM a ORDER BY a.detectedAt DESC",
        enable_cross_partition_query=True
    ))

    return func.HttpResponse(json.dumps(items))
