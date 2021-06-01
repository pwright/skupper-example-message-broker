from flask import Flask, Response, request
from moonisland import MoonIsland, SenderQueue, Message
from threading import Thread
from time import sleep

moon = MoonIsland()
jobs = SenderQueue(moon, "jobs")

flask = Flask("job-requestor")

@flask.errorhandler(Exception)
def error(e):
    flask.logger.error(e)
    return Response(f"Trouble! {e}\n", status=500, mimetype="text/plain")

@flask.route("/send-request", methods=["POST"])
def send_request():
    jobs.send(Message("xxx"))
    return Response("Request sent", mimetype="text/plain")

Thread(target=moon.run, daemon=True).start()

try:
    flask.run(host="0.0.0.0", port=8080)
except KeyboardInterrupt:
    pass
