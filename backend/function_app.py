import azure.functions as func
import datetime, json, hashlib
from datetime import timedelta
from cosmos_client import get_container
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
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

# ---------- CHAT ----------
@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest):
    d = req.get_json()
    msg = d["message"]
    sid = d["studentId"]

    risk = any(w in msg.lower() for w in RISK_WORDS)

    reply = client.chat.completions.create(
        model="tinyllama-1.1b-chat-v1.0",
        messages=[
            {"role":"system","content":"You are a calm emotional support friend. Short replies only."},
            {"role":"user","content":msg}
        ],
        temperature=0.3
    ).choices[0].message.content

    get_container("chat_summaries").create_item({
        "id": str(datetime.datetime.utcnow().timestamp()),
        "studentId": sid,
        "userMessage": msg,
        "botReply": reply,
        "risk": risk
    })

    if risk:
        get_container("risk_alerts").create_item({
            "id": str(datetime.datetime.utcnow().timestamp()),
            "studentId": sid,
            "level": "HIGH",
            "time": datetime.datetime.utcnow().isoformat()
        })

    return func.HttpResponse(json.dumps({"reply": reply}))

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
