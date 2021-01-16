function getWsAddr() {
    if (location.protocol == 'https:') {
        return ("wss://" + location.host + location.pathname + "/ws")
    } else {
        return ("ws://" + location.host + location.pathname + "/ws")
    }
}