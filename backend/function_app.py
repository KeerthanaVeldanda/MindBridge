import azure.functions as func
import datetime
import json
import os
from cosmos_client import get_container
from openai import OpenAI
import logging

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = func.FunctionApp()

# ---------------- ENTER / LOGIN ----------------
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

    student_name = data.get("studentname")
    email = data.get("email")
    password = data.get("password")

    if not student_name or not email or not password:
        return func.HttpResponse(
            json.dumps({"error": "All fields are required"}),
            status_code=400,
            mimetype="application/json"
        )

    users_container = get_container("users")

    users_container.upsert_item({
        "id": email,
        "studentId": email,
        "studentName": student_name,
        "email": email,
        "password": password,
        "createdAt": datetime.datetime.utcnow().isoformat()
    })

    return func.HttpResponse(
        json.dumps({"success": True}),
        status_code=200,
        mimetype="application/json"
    )


# ---------------- CHAT (REAL AI) ----------------
@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest):

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    message = data.get("message")

    if not message:
        return func.HttpResponse(
            json.dumps({"error": "Message is required"}),
            status_code=400,
            mimetype="application/json"
        )

    # ✅ OpenAI Responses API (CORRECT)
    try:
            # Try OpenAI
            response = client.responses.create(
                model="gpt-4o-mini",
                input=message
            )
            reply = response.output_text

    except Exception as ai_error:
        # 🔥 FALLBACK RESPONSE (VERY IMPORTANT)
        logging.error(f"OpenAI failed: {ai_error}")
        reply = (
                "I'm here with you. You’re not alone 🤍\n"
                "Tell me more about what you're feeling."
        )

    # ✅ CORRECT extraction
    reply = response.output_text

    chat_container = get_container("chat_summaries")

    chat_container.create_item({
        "id": str(datetime.datetime.utcnow().timestamp()),
        "studentId": "test-user",
        "userMessage": message,
        "botReply": reply,
        "createdAt": datetime.datetime.utcnow().isoformat()
    })

    return func.HttpResponse(
        json.dumps({"reply": reply}),
        status_code=200,
        mimetype="application/json"
    )
