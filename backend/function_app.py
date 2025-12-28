import azure.functions as func
import datetime
import json
import logging
from openai import OpenAI
import os

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

        


    