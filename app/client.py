from contextlib import closing
from websocket import create_connection

i = 0
with closing(create_connection('ws://0.0.0.0:5000/')) as ws:
    room_id = ws.recv()
    print('http://0.0.0.0:5000/room/' + str(room_id))

    while True:
        try:
            data = ws.recv()
            if data == 'close':
                print('Connection closed')
                break
            print(data)
        except KeyboardInterrupt:
            ws.send('close')
            break
