import { allPlayers, getPlayers } from './rest_api.js';
import {
    initSocket
} from './socket_api.js';


onLoad();

function onLoad() {
    initSocket();
}