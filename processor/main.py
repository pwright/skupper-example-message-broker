from moonisland import MoonIsland, SenderQueue, Message
from threading import Thread
from time import sleep

moon = MoonIsland()
results = SenderQueue(moon, "results")

@moon.receiver("jobs")
def receive_job(message):
    print(f"PROCESSOR: Received job '{message.body}'")

    def process_job():
        sleep(1)

        result = message.body.upper()

        reply = Message(result)
        reply.correlation_id = message.id

        results.send(reply)

        print(f"PROCESSOR: Sent result '{result}'")

    Thread(target=process_job).start()

@moon.sender("status-updates", period=1.0)
def send_status_update(sender):
    sender.send(Message("An update!"))

moon.run()
