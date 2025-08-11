import { allPlayers, getPlayers } from './rest_api.js';
import {
    initSocket
} from './socket_api.js';


onLoad();

function onLoad() {
    initSocket({
        onBuzzersCanceled: handleBuzzersCanceled,
        onBuzzersListening: handleBuzzersListening,
        onBuzzerTimeout: handleBuzzerTimeout,
        onPlayerAnswering: handlePlayerAnswering,
        onPlayerCorrect: handlePlayerCorrect,
        onPlayerIncorrect: handlePlayerIncorrect
    });
}

function handleBuzzersCanceled() {
    
}

function handleBuzzersListening() {
    
}

function handleBuzzerTimeout() {
    
}

function handlePlayerAnswering() {
    
}

function handlePlayerCorrect() {
    
}

function handlePlayerIncorrect() {
    
}
