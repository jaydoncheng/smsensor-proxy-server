class Client {
    websocket;
    client_id;
    socket_open = false;
    interval;
    constructor(address, room_id) {
        var ws = this.websocket = new WebSocket('wss://' + address + '/room/' + room_id);
        this.client_id = Date.now().toString() + Math.floor(Math.random() * 1000000).toString();

        ws.onmessage = (event) => {
            if (event.data === 'close') { socket.close(); }
        };

        ws.onopen = () => {
            this.socket_open = true;
            ws.send(JSON.stringify({
                id: room_id,
                client_id: this.client_id,
            }));
        }

        console.log('Created client', this.client_id, 'for room', room_id, 'at', address);

        const freq = 60;
        this.interval = setInterval(() => this.sendFakeData(), 1000 / freq);
    }

    randValue(min, max) { return Math.random() * (max - min) + min; }
    close() {
        clearInterval(this.interval);
        this.websocket.close();
        this.socket_open = false;
    }

    sendFakeData() {
        if (this.socket_open) {
            const ws = this.websocket;
            ws.send(JSON.stringify({
                client_id: this.client_id,
                type: 'devicemotion',
                timestamp: Date.now(),
                x: this.randValue(-10, 10),
                y: this.randValue(-10, 10),
                z: this.randValue(-10, 10),
                xg: this.randValue(-10, 10),
                yg: this.randValue(-10, 10),
                zg: this.randValue(-10, 10),
            }));

            ws.send(JSON.stringify({
                client_id: this.client_id,
                type: 'deviceorientation',
                timestamp: Date.now(),
                alpha: this.randValue(0, 360),
                beta: this.randValue(-90, 90),
                gamma: this.randValue(-180, 180),
            }));
        }
    }
}

var updateClientCount = () => {
    const clientsDiv = document.getElementById('clients');
    const count = clientsDiv.children.length;
    document.getElementById('client_count').innerHTML = count;
}

var createClientElement = (client) => {
    const el = document.createElement('div');
    const button = document.createElement('button');
    button.innerHTML = 'Close';
    button.onclick = () => {
        client.close();
        el.remove();
        updateClientCount();
    }
    el.innerHTML = client.client_id;
    el.appendChild(button);

    return el;
}

window.addEventListener("load", () => {
    const createButton = document.getElementById('create');
    const addressField = document.getElementById('address');
    const roomIdField = document.getElementById('room_id');
    const clientsDiv = document.getElementById('clients');

    createButton.onclick = () => {
        console.log('Creating client');
        const nr = document.getElementById('nr').value;
        for (let i = 0; i < nr; i++) {
            const address = addressField.value;
            const room_id = roomIdField.value;
            const client = new Client(address, room_id);

            clientsDiv.appendChild(createClientElement(client));
            updateClientCount();
        }
    }

    console.log('Loaded');
});
