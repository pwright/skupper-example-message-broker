from moonisland import MoonIsland, SenderQueue, Message
from threading import Thread
from time import sleep

moon = MoonIsland()
results = SenderQueue(moon, "results")

@moon.receiver("jobs")
def receive_job(message):
    def process_job():
        sleep(1)
        print(f"{message.body} -> {message.body.upper()}")
        results.send(Message(message.body.upper()))

    Thread(target=process_job).start()

@moon.sender("worker-status-updates", period=1.0)
def send_status_update(sender):
    sender.send(Message("An update!"))

moon.run()
