from contextlib import closing
from websocket import create_connection
import qrcodeT
import ast
from prettytable import PrettyTable

ip = 'smsensors.jaydoncheng.me'
with closing(create_connection(f'wss://{ip}/')) as ws:
    print('Connected to server')
    room_id = ast.literal_eval(str(ws.recv()))['id']
    url = f'https://{ip}/room/' +room_id
    print('Scan the QR code to join the room')
    qrcodeT.qrcodeT(url)
    print(url)

    accel_table = PrettyTable()
    orient_table = PrettyTable()

    accel_table.field_names = ['Timestamp', 'X', 'Y', 'Z']
    orient_table.field_names = ['Timestamp', 'Azimuth', 'Pitch', 'Roll']

    i = 0
    while True:
        try:
            data = ws.recv()
            if data == 'close':
                print('Connection closed')
                break

            # clear the screen

            data = ast.literal_eval(str(data))

            # display event data in table format with timestamp
            if 'type' not in data:
                print(data)
                continue
            if data['type'] == 'devicemotion':
                accel_table.clear_rows()
                # truncate values to 5 decimal places
                values = {}
                for key, value in data.items():
                    if isinstance(value, float):
                        values[key] = round(value, 5)
                    else:
                        values[key] = value

                accel_table.add_row([values['timestamp'], values['x'], values['y'], values['z']])
            if data['type'] == 'deviceorientation':
                orient_table.clear_rows()

                values = {'alpha': 0, 'beta': 0, 'gamma': 0}
                for key, value in data.items():
                    if isinstance(value, float):
                        values[key] = round(value, 5)
                    else:
                        values[key] = value

                orient_table.add_row([values['timestamp'], values['alpha'], values['beta'], values['gamma']])

            if i % 10 == 0:
                print(chr(27) + "[2J")
                print(accel_table)
                print(orient_table)
            i += 1

            
        except KeyboardInterrupt:
            ws.send('close')
            break
