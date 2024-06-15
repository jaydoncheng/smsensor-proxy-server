from flask import Flask, render_template, request
from flask_sock import Sock
from dataclasses import dataclass, field
import typing
from datetime import datetime
import uuid
import json

import simple_websocket
# import multiprocessing as mp
# from gevent import monkey
# monkey.patch_all()

app = Flask(__name__)
app.config['SECRET'] = 'secret'
app.config['SOCK_SERVER_OPTIONS'] = {
    'ping_interval': 25,
}

sock = Sock(app)
@dataclass
class Client:
    ws: any

@dataclass
class Room:
    ip: str
    id: uuid.UUID
    last_active: float
    consumers: typing.List[Client] = field(default_factory=list)
    producers: typing.List[Client] = field(default_factory=list)

rooms = {}
def create_room(ip, ws):
    room = Room(ip=ip, id=uuid.uuid4(), last_active=datetime.now().timestamp())

    room.consumers.append(Client(ws))
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
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    room = create_room(ip, ws)

    data = {
        'type': 'newroom',
        'id': str(room.id)
    }
    ws.send(json.dumps(data))
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
    print('New connection to room', id)
    print(f'id: {hex(id(rooms))}')
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

