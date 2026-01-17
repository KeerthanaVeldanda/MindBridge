import azure.functions as func
import datetime, json, hashlib
from datetime import timedelta
from cosmos_client import get_container
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
app = func.FunctionApp()
RISK_WORDS = ["suicide","kill myself","end my life","hopeless","worthless","self harm"]

# ---------- REGISTER ----------
@app.route(route="enter", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def enter(req: func.HttpRequest):
    d = req.get_json()
    email = d["email"]
    users = get_container("users")
    users.upsert_item({
        "id": email,
        "email": email,
        "studentId": email,
        "studentName": d["studentName"],
        "password": hashlib.sha256(d["password"].encode()).hexdigest()
    })
    return func.HttpResponse(json.dumps({"success": True}))

# ---------- LOGIN ----------
@app.route(route="login", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def login(req: func.HttpRequest):
    d = req.get_json()
    users = get_container("users")
    u = users.read_item(d["email"], d["email"])
    if u["password"] != hashlib.sha256(d["password"].encode()).hexdigest():
        return func.HttpResponse(status_code=401)
    return func.HttpResponse(json.dumps(u))

import re

# ---------- CHAT ----------
@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest):
    d = req.get_json()
    msg = d.get("message")
    sid = d.get("studentId")

    if not msg or not sid:
        return func.HttpResponse(
            json.dumps({"error": "Invalid request"}),
            status_code=400,
            mimetype="application/json"
        )

    # Improved risk detection
    risk = any(
        re.search(rf"\b{re.escape(word)}\b", msg.lower())
        for word in RISK_WORDS
    )

    # MindBridge AI response
    response = client.responses.create(
        model="llama-3.1-8b-instant",
        input=[
            {
                "role": "system",
                "content": (
                    "You are MindBridge, a friendly AI mental wellness assistant for students. "
                    "Be supportive, calm, positive, and concise. "
                    "If the user sounds stressed or anxious, respond with empathy and encouragement. "
                    "Never give medical advice."
                )
            },
            {"role": "user", "content": msg}
        ],
        temperature=0.4
    )

    reply = response.output[0].content[0].text

    # Store chat
    get_container("chat_summaries").create_item({
        "id": str(datetime.datetime.utcnow().timestamp()),
        "studentId": sid,
        "userMessage": msg,
        "botReply": reply,
        "risk": risk,
        "time": datetime.datetime.utcnow().isoformat()
    })

    # Store alert if risky
    if risk:
        get_container("risk_alerts").create_item({
            "id": str(datetime.datetime.utcnow().timestamp()),
            "studentId": sid,
            "level": "HIGH",
            "message": msg,
            "time": datetime.datetime.utcnow().isoformat()
        })

    return func.HttpResponse(
        json.dumps({"reply": reply, "risk": risk}),
        mimetype="application/json"
    )

# ---------- MOOD ----------
@app.route(route="mood", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def mood(req: func.HttpRequest):
    d = req.get_json()
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    get_container("moods").upsert_item({
        "id": f"{d['studentId']}_{today}",
        "studentId": d["studentId"],
        "mood": d["mood"],
        "date": today
    })
    return func.HttpResponse(json.dumps({"success": True}))

# ---------- GET MOODS ----------
@app.route(route="moods", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def moods(req: func.HttpRequest):
    sid = req.params.get("studentId")
    items = list(get_container("moods").query_items(
        query="SELECT m.date, m.mood FROM m WHERE m.studentId=@sid",
        parameters=[{"name":"@sid","value":sid}],
        enable_cross_partition_query=True
    ))
    return func.HttpResponse(json.dumps(items))

# ---------- COUNSELLOR ----------
@app.route(route="counsellor/alerts", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def alerts(req: func.HttpRequest):
    items = list(get_container("risk_alerts").query_items(
        query="SELECT * FROM a ORDER BY a.time DESC",
        enable_cross_partition_query=True
    ))
    return func.HttpResponse(json.dumps(items))
