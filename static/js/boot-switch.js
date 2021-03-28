function restart() {
    const request = new XMLHttpRequest();
    request.open('POST', location.pathname + '/restart');
    request.send(null);
}

console.log('Connecting to websocket');
const socket = new WebSocket(getWsAddr())

function sendEvent(event, num) {
    socket.send(JSON.stringify({event: event, num: num}));
}

socket.addEventListener('open', function(ev) {
    console.log('Successfully connected to websocket');
})

socket.addEventListener('message', function(ev) {
    const data = JSON.parse(ev.data);
    const content = document.getElementById('content');
    content.innerHTML = '';
    data.forEach(function(client) {
        const div = document.createElement('div');
        div.className = 'client';
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'name';
        const name_text = document.createTextNode(client.name);
        nameDiv.appendChild(name_text);
        div.appendChild(nameDiv);

        const infoDiv = document.createElement('div');
        infoDiv.className = 'info'

        const input = document.createElement('input');
        input.type = 'button';
        if (client.state != 'closed') {
            input.value = texts.close;
            input.onclick = function () {
                sendEvent('close', client.num);
            }
            input.style = 'border-left-color: #dc322f;'
        } else {
            input.value = texts.start;
            input.onclick = function () {
                sendEvent('start', client.num);
            }
            input.style = 'border-left-color: #43b581;'
        }
        infoDiv.appendChild(input);

        const stateDiv = document.createElement('div');
        stateDiv.className = 'state';
        const stateText = document.createTextNode(texts[client.state]);
        stateDiv.appendChild(stateText);
        infoDiv.appendChild(stateDiv);

        div.appendChild(infoDiv);

        content.appendChild(div);
    });
})