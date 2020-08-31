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

    socket.on("peel", function (data) {
        const player = data["peeling_player"];
        console.log(`Player ${player} has peeled.`);
        document.getElementById("message-banner").innerText = `Player ${player} has peeled.`;

        handleGameUpdate(data);
    });

    socket.on("unsuccessful_peel", function (data) {
        console.log(`Unsuccessful peel.`);
        data["invalid_positions"].forEach(function (position) {
            const invalidPosition = document.getElementById(`space-${position[0]}-${position[1]}`);
            invalidPosition.classList.add("invalid-position");
        })
    });

    socket.on("board_update", function (data) {
        console.log(data);

        handleGameUpdate(data);
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

function handleGameUpdate(data) {
    ///////////////////////////////////////////////////////////////
    // Status update
    document.getElementById("num-players").innerText = data["num_players"];
    document.getElementById("tiles-left").innerText = data["tiles_left"];

    ///////////////////////////////////////////////////////////////
    // Board update
    for (let r = 0; r < data["board"].length; r++) {
        let row = data["board"][r];
        for (let c = 0; c < row.length; c++) {
            let boardTile = row[c];

            if (boardTile == null) {
                boardTile = "&nbsp;"
            }

            document.getElementById(`space-${r}-${c}`).innerHTML = boardTile;
        }
    }

    ///////////////////////////////////////////////////////////////
    // Hand tiles update

    // Clear out all tile buttons to ensure we have a clean state
    $("#tiles-div").empty();

    // Ensure the peel button is enabled or disabled appropriately
    if (data["hand_tiles"].length === 0) {
        const peelButton = document.getElementById("peel-button");
        peelButton.classList.remove("btn-light");
        peelButton.classList.add("btn-primary");
        peelButton.removeAttribute("disabled");
    } else {
        const peelButton = document.getElementById("peel-button");
        peelButton.classList.add("btn-light");
        peelButton.classList.remove("btn-primary");
        peelButton.setAttribute("disabled", "");
    }

    // Create tile buttons for the player's hand
    for (let i = 0; i < data["hand_tiles"].length; i++) {
        const tile = data["hand_tiles"][i];
        const tileElement = document.createElement("BUTTON");
        tileElement.id = `tile-${i}`;
        tileElement.classList.add("btn", "btn-tile", "hand-tile", "btn-light", "rounded-0");
        tileElement.innerText = tile;

        document.getElementById("tiles-div").appendChild(tileElement);
    }
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
        const tileClicked = $(this)[0];

        if ((selectedHandTile != null) && (tileClicked.id === selectedHandTile.id)) {
            // If clicking on the tile that is already selected, deselect it.
            deselectHandTile();
        } else {
            // Otherwise, we have a new selected tile.
            deselectHandTile();

            selectedHandTile = tileClicked;
            selectedHandTile.classList.remove("btn-light");
            selectedHandTile.classList.add("btn-success");
        }
    });

    $("#inner-button-container").on('click', 'button', function () {
        const selectedSpot = $(this)[0];
        const boardPositionRow = parseInt(selectedSpot.id.split("-")[1]);
        const boardPositionCol = parseInt(selectedSpot.id.split("-")[2]);

        if (selectedHandTile == null) {
            // If the spot is empty, don't do anything.
            if (selectedSpot.innerHTML === "&nbsp;") {
                return;
            }

            // Clear invalid positions as the board state has changed.
            clearInvalidPositions();

            // If we do not have a selected tile, remove the tile from the board.
            socket.emit("remove_tile", {
                "room": roomName,
                "board_position": [boardPositionRow, boardPositionCol]
            });
        } else {
            // Clear invalid positions as the board state has changed.
            clearInvalidPositions();

            // If we have a selected tile, add it to the board.
            const handTileIndex = parseInt(selectedHandTile.id.replace("tile-", ""));

            console.log(`Placing ${selectedHandTile.id} at position (${boardPositionRow}, ${boardPositionCol})`);

            deselectHandTile();

            socket.emit("add_tile", {
                "room": roomName,
                "hand_tile_index": handTileIndex,
                "board_position": [boardPositionRow, boardPositionCol]
            })
        }
    });

    $("#peel-button").on('click', function () {
        console.log("Sending peel...");
        socket.emit("peel", {"room": roomName})
    });
}

function clearInvalidPositions() {
    $(".board-tile").each(function (index) {
        $(this)[0].classList.remove("invalid-position");
    })
}

function confirmAndStartNewGame(socket, roomName) {
    const confirmation = confirm("Do you want to start a new game? The current board will be cleared.");
    if (confirmation === true) {
        clearPath();
        console.info("Starting new game...");
        socket.emit('new_game', {'room': roomName});
    }
}
