import azure.functions as func
import datetime
import json
import logging
import hashlib
from cosmos_client import get_container
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

app = func.FunctionApp()

# ---------------- ENTER ----------------
@app.route(route="enter", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def enter(req: func.HttpRequest):

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    student_name = data.get("studentName")
    email = data.get("email")
    password = data.get("password")

    if not student_name or not email or not password:
        return func.HttpResponse(
            json.dumps({"error": "All fields are required"}),
            status_code=400,
            mimetype="application/json"
        )

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    users_container = get_container("users")
    users_container.upsert_item({
        "id": email,
        "studentId": email,
        "studentName": student_name,
        "email": email,
        "password": hashed_password,
        "createdAt": datetime.datetime.utcnow().isoformat()
    })

    return func.HttpResponse(
        json.dumps({"success": True}),
        status_code=200,
        mimetype="application/json"
    )
RISK_KEYWORDS = [
    "suicide", "kill myself", "end my life",
    "worthless", "hopeless", "give up",
    "self harm", "cut myself", "die"
]
# ---------------- CHAT ----------------
@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest):

    try:
        data = req.get_json()
        message = data.get("message")
        student_id = data.get("studentId")

        if not message:
            return func.HttpResponse(
                json.dumps({"reply": "Please type something 🤍"}),
                mimetype="application/json"
            )

        # ---------- RISK DETECTION ----------
        lower_msg = message.lower()
        risk_detected = any(word in lower_msg for word in RISK_KEYWORDS)

        # ---------- AI RESPONSE ----------
        response = client.chat.completions.create(
            model="tinyllama-1.1b-chat-v1.0",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a supportive mental health assistant. "
                        "If the user sounds distressed, respond empathetically "
                        "and encourage seeking help."
                    )
                },
                {"role": "user", "content": message}
            ],
        )

        reply = response.choices[0].message.content.strip()

        # ---------- SAVE CHAT ----------
        chat_container = get_container("chat_summaries")
        chat_container.create_item({
            "id": str(datetime.datetime.utcnow().timestamp()),
            "studentId": student_id,
            "userMessage": message,
            "botReply": reply,
            "riskDetected": risk_detected,
            "createdAt": datetime.datetime.utcnow().isoformat()
        })

        # ---------- CREATE RISK ALERT ----------
        if risk_detected:
            alerts = get_container("risk_alerts")
            alerts.create_item({
                "id": str(datetime.datetime.utcnow().timestamp()),
                "studentId": student_id,
                "riskLevel": "HIGH",
                "reason": "Risky language detected in chat",
                "detectedAt": datetime.datetime.utcnow().isoformat(),
                "status": "NEW"
            })

        return func.HttpResponse(
            json.dumps({"reply": reply}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Chat error: {e}")
        return func.HttpResponse(
            json.dumps({
                "reply": "I'm here with you 🤍 Please try again."
            }),
            mimetype="application/json"
        )
# ---------------- COUNSELLOR ALERTS ----------------
@app.route(route="counsellor/alerts", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_alerts(req: func.HttpRequest):

    alerts_container = get_container("risk_alerts")

    query = """
    SELECT a.studentId, a.riskLevel, a.reason, a.detectedAt
    FROM a
    ORDER BY a.detectedAt DESC
    """

    items = list(alerts_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    return func.HttpResponse(
        json.dumps(items),
        mimetype="application/json"
    )

# ---------------- MOOD ----------------
@app.route(route="mood", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def mood(req: func.HttpRequest):

    try:
        data = req.get_json()
        student_id = data.get("studentId")
        mood = data.get("mood")

        if not student_id or not mood:
            return func.HttpResponse(
                json.dumps({"error": "Missing data"}),
                status_code=400,
                mimetype="application/json"
            )

        mood_container = get_container("moods")

        mood_container.create_item({
            "id": str(datetime.datetime.utcnow().timestamp()),
            "studentId": student_id,
            "mood": mood,
            "date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
            "createdAt": datetime.datetime.utcnow().isoformat()
        })

        return func.HttpResponse(
            json.dumps({"success": True}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Mood error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Could not save mood"}),
            status_code=500,
            mimetype="application/json"
        )

