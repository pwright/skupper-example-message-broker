from moonisland import MoonIsland, SenderQueue, Message
from threading import Thread

moon = MoonIsland("worker-%", debug=True)
responses = SenderQueue(moon, "responses")

@moon.receiver("requests")
def receive_request(message):
    print(f"WORKER: Received request '{message.body}'")

    def process_request():
        text = message.body.upper()

        response = Message(text)
        response.correlation_id = message.id

        responses.send(response)

        print(f"WORKER: Sent response '{text}'")

    Thread(target=process_request).start()

@moon.sender("worker-status", period=1.0)
def send_status_update(sender):
    message = Message("OK")
    message.properties = { "worker_id": "xxx" }

    sender.send(message)

moon.run()
