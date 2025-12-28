import azure.functions as func
import datetime
import json
import logging
from openai import OpenAI
import os
from cosmos_client import get_container

app = func.FunctionApp()

@app.route(route="chat",methods=["POST"],auth_level=func.AuthLevel.ANONYMOUS)
def chat(req:func.HttpRequest):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        data=req.get_json()
        msg=data.get("message")
        if not msg:
            return func.HttpResponse(
                json.dumps({
                    "error":"Please enter the message to respond"
                }),
                status_code=400,
                mimetype="application/json"
            )

        response=client.responses.create(
            model="gpt-5-nano",
            input=[
               {
                  "role": "system",
                   "content": "You are MindBridge, a supportive mental health assistant for students. Do not give medical diagnosis."
               },
               {
                    "role": "user",
                    "content": msg
               }
            ]
        )
        reply=response.output_text
        container=get_container("chat_summaries")
        container.create_item({
            "reply":reply,
            "createdAt":datetime.datetime.isoformat()
        })
        return func.HttpResponse(
            json.dumps({
                "reply":reply
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(
            json.dumps({
               "error":"Internal server error"
            }),
            status_code=500,
            mimetype="application/json"
        )
@app.route(route="chat",methods=["POST"],auth_level=func.AuthLevel.ANONYMOUS)
def enter(req:func.HttpRequest)->func.HttpResponse:
    try:
        data=req.get_json()
        stu_name=data.get("studentname")
        email=data.get("email")
        password=data.get("password")
        if not stu_name or not email or not password:
            return func.HttpResponse(
                json.dumps({
                    "error":"The above details are required to enter"
                }),
                status_code=400,
                mimetype="application/json"
            )
        container=get_container("users")
        container.create_item({
            "studentName":stu_name,
            "email":email,
            "password":password,
            "createdAt":datetime.datetime.isoformat()
        })
        return func.HttpResponse(
            json.dumps({
                "success":True,
                "message":"Login Successful"
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

        


    