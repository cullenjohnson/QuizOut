export let allPlayers = {};
export const restBaseURL = "/api";

export function getPlayers(updateCallback) {
    const getPlayersURL = `${restBaseURL}/players`;

    const xhr = new XMLHttpRequest();
    xhr.open("GET", getPlayersURL);

    xhr.addEventListener("load", (event) => {
        const results = xhr.response;
        for (const player of JSON.parse(results)) {
            allPlayers[player.id] = player;
        }
        if (typeof updateCallback === "function") {
            updateCallback();
        }
    });

    xhr.addEventListener("error", (event) => {
        log.error("Error occurred while getting list of all players.", event);
    });

    xhr.addEventListener("abort", (event) => {
        log.error("Request to get all players was aborted.", event);
    });

    xhr.send();
}

export function savePlayerName(playerName, successCallback) {
    const url = `${restBaseURL}/players`;

    const requestBody = JSON.stringify({name: playerName.trim()});

    const xhr = new XMLHttpRequest();
    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.addEventListener("load", () => successCallback(xhr));
    xhr.addEventListener("error", (event) => {
        log.error("Error occurred while saving player.", event);
    });
    xhr.addEventListener("abort", (event) => {
        log.error("Request to save player was aborted.", event);
    });
    xhr.send(requestBody);
}
