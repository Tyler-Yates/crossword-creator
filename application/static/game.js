let selectedHandTile = null;

$(document).ready(function () {
    const socket = io.connect('https://' + document.domain + ':' + location.port);

    const roomName = document.getElementById('game-name').innerHTML;

    socket.on('connect', function () {
        console.log('Webhook initiated');
        socket.emit('join', {'room': roomName});
    });

    socket.on("game_state", function (data) {
        console.log(data);
    });

    socket.on("board_update", function (data) {
        console.log(data);

        // Board update
        // TODO make the board size pull from the data
        for (let r = 0; r < 25; r++) {
            let row = data["board"][r];
            for (let c = 0; c < 25; c++) {
                let boardTile = row[c];

                if (boardTile == null) {
                    boardTile = "&nbsp;"
                }

                document.getElementById(`space-${r}-${c}`).innerHTML = boardTile;
            }
        }

        // Hand tiles update
        $("#tiles-div").empty();
        for (let i = 0; i < data["hand_tiles"].length; i++) {
            const tile = data["hand_tiles"][i];
            const tileElement = document.createElement("BUTTON");
            tileElement.id = `tile-i`;
            tileElement.classList.add("btn", "btn-tile", "hand-tile", "btn-light", "rounded-0");
            tileElement.innerText = tile;

            document.getElementById("tiles-div").appendChild(tileElement);
        }
    });

    socket.on("game_over", function (data) {
        console.log(data);
    });

    // Add event listeners to the buttons
    add_button_event_listeners(socket, roomName);
});

function end_game() {
    // const guessButtonElement = document.getElementById("guessWordSubmit");
    // const disabledAttribute = document.createAttribute("disabled");
    // guessButtonElement.setAttributeNode(disabledAttribute);
}

function deselectHandTile() {
    if (selectedHandTile != null) {
        selectedHandTile.classList.remove("btn-success");
        selectedHandTile.classList.add("btn-light");
        selectedHandTile = null;
    }
}

// Function that sets up the logic for emitting a socket message when clicking on a button.
function add_button_event_listeners(socket, roomName) {
    console.log("Initializing button event listeners");

    $("#tiles-div").on('click', 'button', function () {
        deselectHandTile();

        selectedHandTile = $(this)[0];
        selectedHandTile.classList.remove("btn-light");
        selectedHandTile.classList.add("btn-success");
    });

    $("#inner-button-container").on('click', 'button', function () {
        if (selectedHandTile != null) {
            const selectedSpot = $(this)[0];

            const handTileIndex = parseInt(selectedHandTile.id.replace("tile-", ""));
            const boardPositionRow = parseInt(selectedSpot.id.split("-")[1]);
            const boardPositionCol = parseInt(selectedSpot.id.split("-")[2]);
            console.log(`Placing ${selectedHandTile.id} at position (${boardPositionRow}, ${boardPositionCol})`);

            deselectHandTile();

            socket.emit("add_tile", {
                "room": roomName,
                "hand_tile_index": handTileIndex,
                "board_position": [boardPositionRow, boardPositionCol]
            })
        }
    });
}

function confirmAndStartNewGame(socket, roomName) {
    const confirmation = confirm("Do you want to start a new game? The current board will be cleared.");
    if (confirmation === true) {
        clearPath();
        console.info("Starting new game...");
        socket.emit('new_game', {'room': roomName});
    }
}
