from flask import Flask, Response, request
from moonisland import MoonIsland, SenderQueue, Message
from threading import Thread
from time import sleep

moon = MoonIsland()
jobs = SenderQueue(moon, "jobs")
results = list()

@moon.receiver("results")
def receive_result(message):
    results.append(message.body)

flask = Flask("job-requestor")

@flask.errorhandler(Exception)
def error(e):
    flask.logger.error(e)
    return Response(f"Trouble! {e}\n", status=500, mimetype="text/plain")

@flask.route("/submit-job", methods=["POST"])
def send_job():
    jobs.send(Message(request.json["text"]))
    return {"status": "OK"}

@flask.route("/get-result")
def get_result():
    return ", ".join(results)

Thread(target=moon.run, daemon=True).start()

try:
    flask.run(host="0.0.0.0", port=8080)
except KeyboardInterrupt:
    pass
