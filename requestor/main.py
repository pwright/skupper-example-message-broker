from flask import Flask, Response, request
from moonisland import MoonIsland, SenderQueue, Message
from threading import Thread
from time import sleep
from uuid import uuid4

moon = MoonIsland()
jobs = SenderQueue(moon, "jobs")
results = dict()

@moon.receiver("results")
def receive_result(message):
    results[str(message.correlation_id)] = message.body
    print(f"REQUESTOR: Received result '{message.body}'")

flask = Flask("job-requestor")

@flask.errorhandler(Exception)
def error(e):
    flask.logger.error(e)
    return Response(f"Trouble! {e}\n", status=500, mimetype="text/plain")

@flask.route("/submit-job", methods=["POST"])
def submit_job():
    text = request.form["text"]

    message = Message(text)
    message.id = uuid4()
    message.reply_to = "results"

    jobs.send(message)

    print(f"REQUESTOR: Submitted job '{text}'")

    return \
        f"Job ID: {message.id}\n" \
        f"Text: {text}\n" \
        f"Status: OK\n"

@flask.route("/get-result")
def get_result():
    job_id = request.args["job"]

    try:
        return results[job_id]
    except KeyError:
        return "[No result]"

Thread(target=moon.run, daemon=True).start()

try:
    flask.run(host="0.0.0.0", port=8080)
except KeyboardInterrupt:
    pass
