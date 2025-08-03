export let socket = null;

export function initSocket({ onConnect, onUpdateBuzzerClient, onPlayerAnswering, onBuzzersListening, onBuzzersCanceled } = {}) {
    socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function () {
        socket.emit('adminClientConnected');
        console.log('Connected to the server');
        if (typeof onConnect === 'function') {
            onConnect();
        }
    });

    socket.on('response', function (data) {
        console.log('Server says: ' + data);
    });

    socket.on('updateBuzzerClient', function(data) {
        if (typeof onUpdateBuzzerClient === 'function') {
            onUpdateBuzzerClient(JSON.parse(data));
        }
    });

    socket.on('playerAnswering', function(playerKey) {
        if (typeof onPlayerAnswering === 'function') {
            onPlayerAnswering(playerKey);
        }
    });

    socket.on('buzzersListening', function(data) {
        if (typeof onBuzzersListening === 'function') {
            onBuzzersListening(data);
        }
    });

    socket.on('buzzersCanceled', function(data) {
        if (typeof onBuzzersCanceled === 'function') {
            onBuzzersCanceled(data);
        }
    });
}

export function emitResetBuzzers(data) {
    socket.emit('resetBuzzers', data);
}

export function emitPlayerCorrect(playerKey) {
    socket.emit('playerCorrect', playerKey);
}

export function emitPlayerIncorrect(playerKey) {
    socket.emit('playerIncorrect', playerKey);
}

export function emitBuzzerTimeout() {
    socket.emit('buzzerTimeout');
}
