from contextlib import closing
from websocket import create_connection

ip = '104.248.92.31'
i = 0
with closing(create_connection(f'ws://{ip}/')) as ws:
    room_id = ws.recv()
    print(f'http://{ip}/room/' + str(room_id))

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
