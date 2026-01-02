import azure.functions as func
import datetime
import json
import logging
from cosmos_client import get_container

from openai import OpenAI

# ✅ LM Studio local OpenAI-compatible client
client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"  
)

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


# ---------------- CHAT ----------------
@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest):

    try:
        data = req.get_json()
        message = data.get("message")

        if not message:
            return func.HttpResponse(
                json.dumps({"reply": "Please type something so I can listen 🤍"}),
                status_code=200,
                mimetype="application/json"
            )

        # ✅ CALL LOCAL LM STUDIO MODEL
        response = client.chat.completions.create(
            model="tinyllama-1.1b-chat-v1.0",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are MindBridge, a supportive mental health assistant for students. "
                        "Be empathetic, calm, and encouraging. Do not give medical diagnoses."
                    )
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=200
        )

        reply = response.choices[0].message.content.strip()

        # ✅ SAVE CHAT
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

    except Exception as e:
        logging.error(f"Chat error: {e}")
        return func.HttpResponse(
            json.dumps({
                "reply": (
                    "I'm here with you 🤍 "
                    "Something went wrong, but you can try again."
                )
            }),
            status_code=200,
            mimetype="application/json"
        )
