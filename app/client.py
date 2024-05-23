from contextlib import closing
from websocket import create_connection
import qrcodeT

ip = 'smsensors.jaydoncheng.me'
with closing(create_connection(f'wss://{ip}/')) as ws:
    print('Connected to server')
    room_id = ws.recv()
    url = f'https://{ip}/room/' + str(room_id)
    print('Scan the QR code to join the room')
    qrcodeT.qrcodeT(url)
    print(url)

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
