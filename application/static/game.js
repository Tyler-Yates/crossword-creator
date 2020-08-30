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

// Function that sets up the logic for emitting a socket message when clicking on a button.
function add_button_event_listeners(socket, roomName) {
    console.log("Initializing button event listeners");
    $("#tiles-div").on('click', 'button', function() {
        if (selectedHandTile != null) {
            selectedHandTile.classList.remove("btn-success");
            selectedHandTile.classList.add("btn-light");
        }

        selectedHandTile = $(this)[0];
        selectedHandTile.classList.remove("btn-light");
        selectedHandTile.classList.add("btn-success");
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
