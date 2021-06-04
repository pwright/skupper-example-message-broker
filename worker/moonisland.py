import collections as _collections
import proton as _proton
import proton.handlers as _proton_handlers
import proton.reactor as _proton_reactor
import traceback as _traceback
import uuid as _uuid

class MoonIsland:
    def __init__(self, id=None, debug=False):
        self._debug = debug

        self._receivers = list()
        self._senders = list()
        self._sender_queues = list()

        self._events = _proton_reactor.EventInjector()
        self._container = _proton_reactor.Container(_Handler(self))
        self._container.selectable(self._events)

        if id is not None:
            if "%" in id:
                id = id.replace("%", str(_uuid.uuid4())[-12:], 1)

            self._container.container_id = id

        self.debug("Created container '{}'", self._container.container_id)

    @property
    def id(self):
        return self._container.container_id

    def debug(self, message, *args):
        if not self._debug:
            return

        message = message.format(*args)

        print(f"moonisland: {message}")

    def receiver(app, address):
        class _Receiver:
            def __init__(self, function):
                self.function = function
                self.address = address

                app._receivers.append(self)

            def __call__(self, message):
                self.function(message)

        return _Receiver

    def sender(app, address, period):
        class _Sender:
            def __init__(self, function):
                self.function = function
                self.address = address
                self.period = period

                app._senders.append(self)

            def __call__(self, sender):
                self.function(sender)

        return _Sender

    def run(self):
        try:
            self._container.run()
        except KeyboardInterrupt:
            pass
        except:
            _traceback.print_exc()
        finally:
            self._events.close()

class SenderQueue:
    def __init__(self, app, address):
        self.app = app
        self.address = address

        self._items = _collections.deque()
        self._event = None

        self.app._sender_queues.append(self)

    def _bind(self, sender):
        assert self._event is None
        self._event = _proton_reactor.ApplicationEvent("queue_put", subject=sender)

    def _get(self):
        try:
            return self._items.popleft()
        except IndexError:
            return None

    def send(self, message):
        assert self._event is not None
        self._items.append(message)
        self.app._events.trigger(self._event)

class Message(_proton.Message):
    pass

class _TimerHandler(_proton_reactor.Handler):
    def __init__(self, sender):
        super().__init__()
        self._sender = sender

    def on_timer_task(self, event):
        self._sender(self._sender._pn_sender)

        event.container.schedule(self._sender.period, self)

class _Handler(_proton_handlers.MessagingHandler):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def on_start(self, event):
        conn = event.container.connect()

        for mi_sender_queue in self.app._sender_queues:
            pn_sender = event.container.create_sender(conn, mi_sender_queue.address)
            pn_sender.mi_sender_queue = mi_sender_queue

            mi_sender_queue._bind(pn_sender)

            self.app.debug("Created queue sender for address '{}'", mi_sender_queue.address)

        for mi_sender in self.app._senders:
            pn_sender = event.container.create_sender(conn, mi_sender.address)
            pn_sender.mi_sender = mi_sender
            mi_sender._pn_sender = pn_sender

            event.container.schedule(mi_sender.period, _TimerHandler(mi_sender))

            self.app.debug("Created sender for address '{}'", mi_sender.address)

        for mi_receiver in self.app._receivers:
            pn_receiver = event.container.create_receiver(conn, mi_receiver.address)
            pn_receiver.mi_receiver = mi_receiver

            self.app.debug("Created receiver for address '{}'", mi_receiver.address)

    # def on_connection_opening(self, event):
    #     # XXX I think this should happen automatically.  I seem to need it for the server case.
    #     event.connection.container = event.container.container_id

    def on_connection_opened(self, event):
        self.app.debug("Connected to {}", event.connection.url)

    def on_connection_error(self, event):
        self.app.debug("Failed connecting to {}", event.connection.url)

    def on_transport_error(self, event):
        self.app.debug("Failed connecting to {}", event.connection.url)

    def on_message(self, event):
        message = event.message
        pn_receiver = event.link

        self.app.debug("Received message from '{}'", pn_receiver.source.address)

        pn_receiver.mi_receiver(message)

    def on_queue_put(self, event):
        pn_sender = event.subject
        mi_sender_queue = pn_sender.mi_sender_queue

        while True or pn_sender.credit:
            message = mi_sender_queue._get()

            if message is None:
                break

            pn_sender.send(message)

            self.app.debug("Sent message to '{}'", pn_sender.target.address)
