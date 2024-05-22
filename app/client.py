from contextlib import closing
from websocket import create_connection

ip = 'smsensors.jaydoncheng.me'
with closing(create_connection(f'ws://{ip}:8000/')) as ws:
    print('Connected to server')
    room_id = ws.recv()
    print(f'https://{ip}/room/' + str(room_id))

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
