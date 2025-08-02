import { allPlayers, getPlayers, savePlayerName } from './rest_api.js';
import {
    initSocket,
    emitResetBuzzers,
    emitPlayerCorrect,
    emitPlayerIncorrect,
    emitBuzzerTimeout
} from './socket_api.js';

let buzzerClientInfo = null;
let lastPlayerKey = null;
let buzzerTimer = null;
let buzzerTimerMS = 0;
let inactiveTeams = [];
let buzzerPlayers = {};
const BUZZER_PLAYERS_STORAGE_KEY = 'buzzerPlayers';
loadBuzzerPlayersFromLocalStorage();
const colors = [
    "red",
    "blue",
    "yellow",
    "orange",
    "green",
    "violet"
];
let submitPlayerNamesRefreshTimeout = null;

const playerBuzzedModal = new bootstrap.Modal(document.getElementById('playerBuzzedModal'));
const editBuzzerPlayersModal = new bootstrap.Modal(document.getElementById('editBuzzerPlayersModal'), {backdrop: false, focus: false});
const playerNameSpan = document.getElementById('playerNameSpan');
const activateButton = document.getElementById('activateBuzzersBtn');
const statusP = document.getElementById('statusP');
const buzzerTimerP = document.getElementById('buzzerTimerP');

function handleUpdateBuzzerClient(data) {
    buzzerClientInfo = data;
    updateBuzzerPlayerListsHTML();
}

function handlePlayerAnswering(playerKey) {
    lastPlayerKey = playerKey;

    playerNameSpan.innerHTML = getPlayerName(playerKey) || `Player ${playerKey}`;
    playerNameSpan.classList = `badge background-color-${getPlayerColor(playerKey)}`;
    playerBuzzedModal.show();
    stopBuzzerTimer();
}

initSocket({
    onConnect: uiReady,
    onUpdateBuzzerClient: handleUpdateBuzzerClient,
    onPlayerAnswering: handlePlayerAnswering
});

function uiReady() {
    activateButton.removeAttribute("disabled");
    hideModal(playerBuzzedModal);
    statusP.innerHTML = '💤 Buzzers Inactive';
}

function resetBuzzers(inactiveTeamsA) {
    const data = JSON.stringify({inactive_teams: inactiveTeamsA});
    inactiveTeams = inactiveTeamsA;
    emitResetBuzzers(data);
    startBuzzerTimer();
    activateButton.setAttribute("disabled", "");
}

function playerCorrect() {
    emitPlayerCorrect(lastPlayerKey);
    uiReady();
}

function playerIncorrect() {
    emitPlayerIncorrect(lastPlayerKey);
    hideModal(playerBuzzedModal);
    playerTeam = buzzerClientInfo['teamBuzzerInfo']['buzzerTeams'][lastPlayerKey];

    inactiveTeams.push(playerTeam);

    if (inactiveTeams.length < buzzerClientInfo['teamBuzzerInfo']['teams'].length) {
        startBuzzerTimer();
    } else {
        statusP.innerHTML = `
                <span class="text-danger-emphasis">❌ Each team gave an incorrect response to the last question.</span>
                <br>
                💤 Buzzers Inactive`;
        activateButton.removeAttribute("disabled");
    }
}

function buzzerTimeout() {
    emitBuzzerTimeout();
    stopBuzzerTimer();
    uiReady();
}

function startBuzzerTimer() {
    buzzerTimerP.classList.remove('d-none');
    buzzerTimerP.innerHTML = `<span class="text-primary-emphasis">0.0 seconds</span>`;
    statusP.innerHTML = `
            <span class="text-primary-emphasis">
                <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
                </div>
                Waiting for players to buzz...
            </span>`;

    buzzerTimerMS = 0;
    buzzerTimer = window.setInterval(() => {
        buzzerTimerMS += 100;
        const buzzerTimerSeconds = buzzerTimerMS / 1000;
        let colorClass = "";

        if (buzzerTimerSeconds <= 10) {
            colorClass = 'text-primary-emphasis';
        } else if (buzzerTimerSeconds <= 20) {
            colorClass = 'text-warning-emphasis';
        } else {
            colorClass = 'text-danger-emphasis';
        }

        buzzerTimerP.innerHTML = `<span class="${colorClass}">${buzzerTimerSeconds.toFixed(1)} seconds</span>`;
        statusP.querySelector('span').classList = [colorClass];
    }, 100);
}

function stopBuzzerTimer() {
    window.clearInterval(buzzerTimer);
    buzzerTimerP.classList.add('d-none');
}

function updateBuzzerPlayerListsHTML() {
    const playersList = document.getElementById('playersList');
    playersList.innerHTML = '';

    const playersListFormContent = document.getElementById('playersListFormContent');
    playersListFormContent.innerHTML = '';

    if (buzzerClientInfo == null) {
        return;
    }

    const buzzerTeams = buzzerClientInfo.teamBuzzerInfo.buzzerTeams;
    const teams = buzzerClientInfo.teamBuzzerInfo.teams;

    playersList.innerHTML = `${Object.keys(buzzerTeams).length} players connected. `;

    for (let i = 0, team = teams[0]; i < teams.length; team = teams[++i]) {
        let teamFormHTML = `<h5>Team ${i + 1}</h5>`;
        const buzzers = Object.keys(buzzerTeams).filter(key => buzzerTeams[key] === team);
        for (let buzzer of buzzers) {
            const playerColor = getPlayerColor(buzzer);
            const playerName = getPlayerName(buzzer);
            teamFormHTML += `
                    <div class="input-group mb-3">
                        <span class="input-group-text background-color-${playerColor}" id="basic-addon-${buzzer}" >Player ${buzzer}</span>
                        <input id="playerName-${buzzer}" type="text" class="form-control"
                            placeholder="Player Name" aria-label="Player ${buzzer} Name" aria-describedby="basic-addon-${buzzer}" value="${escapeHTML(playerName)}"
                            list="playerNamesDatalist">
                    </div>`;
        }

        playersListFormContent.innerHTML += teamFormHTML;
    }

    const playerNameList = document.getElementById('playerNamesDatalist');
    let playerListHTML = '';
    const playerNames = Object.values(allPlayers).map(p => p.name).sort();
    for (let playerName of playerNames) {
        playerListHTML += `<option value="${playerName}">`;
    }
    playerNameList.innerHTML = playerListHTML;
}

function getPlayerColor(buzzer) {
    const colorIndex = (parseInt(buzzer) - 1) % 6;
    return colors[colorIndex];
}

function getPlayerName(buzzer) {
    if (!(buzzer in buzzerPlayers)) {
        return '';
    }

    return buzzerPlayers[buzzer].name;
}

function escapeHTML(unsafe) {
    return unsafe
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function savePlayerNames() {
    hideModal(editBuzzerPlayersModal);
    const buzzerTeams = buzzerClientInfo.teamBuzzerInfo.buzzerTeams;
    for (const [buzzer, team] of Object.entries(buzzerTeams)) {
        const playerName = document.getElementById(`playerName-${buzzer}`).value.trim();
        if (playerName != '') {
            const buzzerClone = buzzer;
            savePlayerName(playerName, (xhr) => {
                const playerResponse = xhr.response;
                const player = JSON.parse(playerResponse);
                buzzerPlayers[buzzerClone] = player;
                allPlayers[player.id] = player;
                saveBuzzerPlayersToLocalStorage();

                if (submitPlayerNamesRefreshTimeout != null)
                    window.clearTimeout(submitPlayerNamesRefreshTimeout);
                submitPlayerNamesRefreshTimeout = window.setTimeout(() => updateBuzzerPlayerListsHTML(), 1000);
            });
        }
    }
}

function saveBuzzerPlayersToLocalStorage() {
    window.localStorage.setItem(BUZZER_PLAYERS_STORAGE_KEY, JSON.stringify(buzzerPlayers));
}

function loadBuzzerPlayersFromLocalStorage() {
    const stored = window.localStorage.getItem(BUZZER_PLAYERS_STORAGE_KEY);
    if (stored) {
        try {
            buzzerPlayers = JSON.parse(stored);
            for (const player of Object.values(buzzerPlayers)) {
                if (player && player.id !== undefined) {
                    allPlayers[player.id] = player;
                }
            }
        } catch (e) {
            console.warn('Failed to load buzzer players from localStorage', e);
        }
    }
}

function hideModal(modal) {
    const activeElement = document.activeElement;
    if (activeElement) {
        activeElement.blur();
    }

    modal.hide();
}

// expose for inline event handlers
window.resetBuzzers = resetBuzzers;
window.playerCorrect = playerCorrect;
window.playerIncorrect = playerIncorrect;
window.buzzerTimeout = buzzerTimeout;
window.submitPlayerNames = savePlayerNames;
window.editBuzzerPlayersModal = editBuzzerPlayersModal;
window.uiReady = uiReady;
window.hideModal = hideModal;

// initialize
getPlayers(updateBuzzerPlayerListsHTML);
