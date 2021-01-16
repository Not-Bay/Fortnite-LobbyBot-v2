console.log('Connecting to websocket');
const socket = new WebSocket(getWsAddr())

socket.addEventListener('open', function(ev) {
    console.log('Successfully connected to websocket');
})

socket.addEventListener('message', function(ev) {
    const data = JSON.parse(ev.data);
    const content = document.getElementById('content');
    content.innerHTML = '';
    data.forEach(client => {
        const a = document.createElement('a');
        a.href = location.pathname + '/' + client.num;
        const name_text = document.createTextNode(client.name);
        a.appendChild(name_text);
        content.appendChild(a);
    });
})