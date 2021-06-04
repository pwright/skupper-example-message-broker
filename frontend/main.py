from flask import Flask, Response, request, jsonify
from moonisland import MoonIsland, SenderQueue, Message
from threading import Thread, Lock
from time import sleep
from uuid import uuid4

import logging
logging.basicConfig(level=logging.INFO)

# AMQP

moon = MoonIsland("frontend-%", debug=True)
requests = SenderQueue(moon, "requests")
responses = dict()
worker_status = dict()
lock = Lock()

@moon.receiver("responses")
def receive_responses(message):
    text = message.body

    with lock:
        responses[str(message.correlation_id)] = text

    print(f"FRONTEND: Received response '{text}'")

@moon.receiver("worker-status")
def receive_worker_status(message):
    worker_id = message.properties["worker_id"]
    status = message.body

    with lock:
        worker_status[worker_id] = status

Thread(target=moon.run, daemon=True).start()

# HTTP

flask = Flask("frontend")

@flask.errorhandler(Exception)
def error(e):
    flask.logger.error(e)
    return Response(f"Trouble! {e}\n", status=500, mimetype="text/plain")

@flask.route("/api/send-request", methods=["POST"])
def send_request():
    text = request.form["text"]

    message = Message(text)
    message.id = uuid4()
    message.reply_to = "responses"

    requests.send(message)

    print(f"FRONTEND: Sent request '{text}'")

    return {
        "id": str(message.id),
        "text": text,
        "error": None,
    }

@flask.route("/api/responses")
def get_responses():
    with lock:
        return responses

@flask.route("/api/worker-status")
def get_worker_status():
    with lock:
        return worker_status

try:
    flask.run(host="0.0.0.0", port=8080)
except KeyboardInterrupt:
    pass
