import collections as _collections
import proton as _proton
import proton.handlers as _proton_handlers
import proton.reactor as _proton_reactor

class MoonIsland:
    def __init__(self, debug=False):
        self._debug = debug

        self._receivers = list()
        self._senders = list()
        self._sender_queues = list()

        self._events = _proton_reactor.EventInjector()
        self._container = _proton_reactor.Container(_Handler(self))
        self._container.selectable(self._events)

    def receiver(app, address):
        class _Receiver:
            def __init__(self, function):
                self._function = function
                self._address = address

                app._receivers.append(self)

            def __call__(self, message):
                self._function(message)

        return _Receiver

    def sender(app, address, period):
        class _Sender:
            def __init__(self, function):
                self._function = function
                self._address = address
                self._period = period

                app._senders.append(self)

            def __call__(self, sender):
                self._function(sender)

        return _Sender

    def run(self):
        try:
            self._container.run()
        except KeyboardInterrupt:
            pass
        finally:
            self._events.close()

class SenderQueue:
    def __init__(self, app, address):
        self._app = app
        self._address = address
        self._items = _collections.deque()
        self._event = None

        self._app._sender_queues.append(self)

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
        self._app._events.trigger(self._event)

class Message(_proton.Message):
    pass

class _TimerHandler(_proton_reactor.Handler):
    def __init__(self, sender):
        super().__init__()
        self._sender = sender

    def on_timer_task(self, event):
        self._sender(self._sender._pn_sender)

        event.container.schedule(self._sender._period, self)

class _Handler(_proton_handlers.MessagingHandler):
    def __init__(self, app):
        super().__init__()
        self._app = app

    def on_start(self, event):
        conn = event.container.connect()

        for mi_sender_queue in self._app._sender_queues:
            pn_sender = event.container.create_sender(conn, mi_sender_queue._address)
            pn_sender.mi_sender_queue = mi_sender_queue

            mi_sender_queue._bind(pn_sender)

        for mi_sender in self._app._senders:
            pn_sender = event.container.create_sender(conn, mi_sender._address)
            pn_sender.mi_sender = mi_sender
            mi_sender._pn_sender = pn_sender

            event.container.schedule(mi_sender._period, _TimerHandler(mi_sender))

        for mi_receiver in self._app._receivers:
            pn_receiver = event.container.create_receiver(conn, mi_receiver._address)
            pn_receiver.mi_receiver = mi_receiver

    def on_message(self, event):
        message = event.message
        pn_receiver = event.link

        pn_receiver.mi_receiver(message)

    def on_queue_put(self, event):
        pn_sender = event.subject
        mi_sender_queue = pn_sender.mi_sender_queue

        while pn_sender.credit:
            message = mi_sender_queue._get()

            if message is None:
                break

            pn_sender.send(message)
