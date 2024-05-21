from flask import Flask, render_template, request, redirect, url_for
from flask_sock import Sock
from dataclasses import dataclass, field
import typing
from datetime import datetime
import uuid

import simple_websocket

app = Flask(__name__)
app.config['SECRET'] = 'secret'
app.config['SOCK_SERVER_OPTIONS'] = {
    'ping_interval': 25,
}

sock = Sock(app)


"""
pc client is the receiver
mobile client is the sender

pc client sends a request to /new to create a new room
server responds with a room id
pc client sends a request to /join/<id> to join the room
pc client joins websocket room with room id
mobile client sends a request to /join/<id> to join the room
mobile client joins websocket room with room id
mobile client sends a message to the websocket room
pc client receives the message
"""

@dataclass
class Client:
    ws: any

@dataclass
class Room:
    id: uuid.UUID
    last_active: float
    consumers: typing.List[Client] = field(default_factory=list)
    producers: typing.List[Client] = field(default_factory=list)

rooms : typing.Dict[str, Room] = {}
def create_room():
    room = Room(id=uuid.uuid4(), last_active=datetime.now().timestamp())
    rooms[str(room.id)] = room
    return room

def close_room(room):
    for client in room.consumers:
        client.ws.send('close')
    for client in room.producers:
        client.ws.send('close')
    del rooms[str(room.id)]

@sock.route('/')
def new(ws):
    for room in rooms.values():
        if datetime.now().timestamp() - room.last_active > 60*30:
            del rooms[str(room.id)]

    room = create_room()
    room.consumers.append(Client(ws))

    ws.send(str(room.id))
    while True:
        try:
            data = ws.receive()
            if data == 'close':
                close_room(room)
                break
        except simple_websocket.ConnectionClosed:
            # Closes the entire room, including all clients
            print('Connection closed')
            close_room(room)
            break
    
@app.route('/room/<id>', methods=['GET'])
def join(id):
    return render_template('join.html', id=id)

@sock.route('/room/<id>')
def room(ws, id):
    if id not in rooms:
        ws.send('close')
        return
    room = rooms[id]
    room.producers.append(Client(ws))
    while True:
        try:
            data = ws.receive()
            if data == 'close':
                room.producers.remove(Client(ws))
                break
            for client in room.consumers:
                client.ws.send(data)
        except simple_websocket.ConnectionClosed:
            room.producers.remove(Client(ws))
            break

if __name__ == '__main__':
    app.run()

