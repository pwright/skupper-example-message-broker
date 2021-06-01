from moonisland import MoonIsland, SenderQueue, Message
from threading import Thread
from time import sleep

moon = MoonIsland()
# notifications = SenderQueue(app, "notifications")

@moon.receiver("jobs")
def receive_job(message):
    def worker():
        sleep(1)
        print(f"{message.body} -> {message.body.upper()}")
        # notifications.send(Message(f"{message.body} -> {message.body.upper()}"))

    Thread(target=worker).start()

moon.run()
