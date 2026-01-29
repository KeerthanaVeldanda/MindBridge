import azure.functions as func
import datetime, json, hashlib, re, os
from cosmos_client import get_container
from openai import OpenAI

# ---------------- AI CLIENT ----------------
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# ---------------- APP ----------------
app = func.FunctionApp()

# ---------------- RISK WORDS ----------------
RISK_WORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "hopeless",
    "worthless",
    "self harm",
    "anxious",
    "panic",
]

# ======================================================
# REGISTER (Student / Counsellor)
# ======================================================
@app.route(route="enter", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def enter(req: func.HttpRequest):
    d = req.get_json()
    email = d["email"]
    role = d.get("role", "student").lower()

    users = get_container("users")

    users.upsert_item({
        "id": email,
        "email": email,
        "userId": email,
        "name": d["studentName"],
        "password": hashlib.sha256(d["password"].encode()).hexdigest(),
        "role": role,  # student / counsellor
        "createdAt": datetime.datetime.utcnow().isoformat()
    })

    return func.HttpResponse(json.dumps({"success": True}))


# ======================================================
# LOGIN
# ======================================================
@app.route(route="login", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def login(req: func.HttpRequest):
    d = req.get_json()
    users = get_container("users")

    try:
        user = users.read_item(d["email"], d["email"])
    except:
        return func.HttpResponse(
            json.dumps({"error": "User not found"}),
            status_code=404
        )

    if user["password"] != hashlib.sha256(d["password"].encode()).hexdigest():
        return func.HttpResponse(
            json.dumps({"error": "Invalid credentials"}),
            status_code=401
        )

    return func.HttpResponse(json.dumps(user))


# ======================================================
# CHAT (STUDENT AI CHAT)
# ======================================================
@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest):
    d = req.get_json()
    msg = d.get("message")
    sid = d.get("studentId")

    if not msg or not sid:
        return func.HttpResponse(
            json.dumps({"error": "Invalid request"}),
            status_code=400
        )

    # -------- Risk Detection --------
    risk = any(
        re.search(rf"\b{re.escape(word)}\b", msg.lower())
        for word in RISK_WORDS
    )

    # -------- AI Response --------
    response = client.responses.create(
        model="llama-3.1-8b-instant",
        input=[
            {
                "role": "system",
                "content": (
                    "You are MindBridge, a calm and friendly AI mental wellness assistant. "
                    "Be empathetic, supportive, and concise. "
                    "Never provide medical advice."
                )
            },
            {"role": "user", "content": msg}
        ],
        temperature=0.4
    )

    reply = response.output[0].content[0].text

    # -------- Store Chat --------
    get_container("chat_summaries").create_item({
        "id": str(datetime.datetime.utcnow().timestamp()),
        "studentId": sid,
        "userMessage": msg,
        "botReply": reply,
        "risk": risk,
        "time": datetime.datetime.utcnow().isoformat()
    })

    # -------- Create Risk Alert --------
    if risk:
        get_container("risk_alerts").create_item({
            "id": str(datetime.datetime.utcnow().timestamp()),
            "studentId": sid,
            "message": msg,
            "level": "HIGH",
            "resolved": False,
            "source": "chat",
            "time": datetime.datetime.utcnow().isoformat()
        })

    return func.HttpResponse(
        json.dumps({"reply": reply, "risk": risk}),
        mimetype="application/json"
    )


# ======================================================
# MOOD LOG
# ======================================================
@app.route(route="mood", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def mood(req: func.HttpRequest):
    d = req.get_json()
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    get_container("moods").upsert_item({
        "id": f"{d['studentId']}_{today}",
        "studentId": d["studentId"],
        "mood": d["mood"],
        "note": d.get("note", ""),
        "date": today
    })

    return func.HttpResponse(json.dumps({"success": True}))


# ======================================================
# GET MOODS (STUDENT DASHBOARD)
# ======================================================
@app.route(route="moods", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def moods(req: func.HttpRequest):
    sid = req.params.get("studentId")

    items = list(
        get_container("moods").query_items(
            query="SELECT m.date, m.mood, m.note FROM m WHERE m.studentId=@sid",
            parameters=[{"name": "@sid", "value": sid}],
            enable_cross_partition_query=True
        )
    )

    return func.HttpResponse(json.dumps(items))


# ======================================================
# COUNSELLOR – GET ACTIVE ALERTS
# ======================================================
@app.route(route="counsellor/alerts", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def counsellor_alerts(req: func.HttpRequest):
    alerts = list(
        get_container("risk_alerts").query_items(
            query="SELECT * FROM a WHERE a.resolved=false ORDER BY a.time DESC",
            enable_cross_partition_query=True
        )
    )

    return func.HttpResponse(json.dumps(alerts))


# ======================================================
# COUNSELLOR – MARK ALERT RESOLVED
# ======================================================
@app.route(route="counsellor/resolve", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def resolve_alert(req: func.HttpRequest):
    d = req.get_json()
    alert_id = d["id"]

    container = get_container("risk_alerts")
    alert = container.read_item(alert_id, partition_key=alert_id)

    alert["resolved"] = True
    alert["resolvedAt"] = datetime.datetime.utcnow().isoformat()

    container.replace_item(alert["id"], alert)

    return func.HttpResponse(json.dumps({"success": True}))
