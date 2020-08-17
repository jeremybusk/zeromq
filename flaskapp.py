#!/usr/bin/env python3
import zmq
from flask import Flask
from threading import Thread

HOST = '127.0.0.1'
PORT = 9090
TASK_SOCKET = zmq.Context().socket(zmq.REQ)
TASK_SOCKET.connect('tcp://{}:{}'.format(HOST, PORT))
app = Flask("app")


@app.route("/start")
def start():
    TASK_SOCKET.send_json({"command": "start"})
    results = TASK_SOCKET.recv_json()
    return f"starting {results}"


@app.route("/pause")
def pause():
    TASK_SOCKET.send_json({"command": "pause"})
    results = TASK_SOCKET.recv_json()
    return f"pausing {results}"


class Worker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self.active = True

    def run(self):
        self._socket.bind('tcp://{}:{}'.format(HOST, PORT))
        self._socket.setsockopt(zmq.RCVTIMEO, 500)
        while self.active:
            ev = self._socket.poll(1000)
            if ev:
                rec = self._socket.recv_json()
                self._socket.send_json({"response": "ok", "payload": rec})


if __name__ == "__main__":
    worker = Worker()
    worker.start()
    app.run()
