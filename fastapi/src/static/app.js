const boardSize = 20;
let gameId = null;
let gameInterval = null;

function initializeBoard() {
  const board = document.getElementById("snake-board");
  board.innerHTML = "";
  for (let row = 0; row < boardSize; row++) {
    const rowElement = document.createElement("tr");
    for (let col = 0; col < boardSize; col++) {
      const cell = document.createElement("td");
      cell.id = `cell-${row}-${col}`;
      rowElement.appendChild(cell);
    }
    board.appendChild(rowElement);
  }
}

function startGame() {
  fetch("/snake/start", { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      gameId = data.game_id;
      updateBoard(data.snake, data.apple);
      document.getElementById("score").innerText = `Score: ${data.score}`;
      if (gameInterval) clearInterval(gameInterval);
      gameInterval = setInterval(() => moveSnake(data.direction), 500);
    });
}

function moveSnake(direction) {
  fetch("/snake/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ game_id: gameId, direction: direction }),
  })
    .then((res) => res.json())
    .then((data) => {
      updateBoard(data.snake, data.apple);
      document.getElementById("score").innerText = `Score: ${data.score}`;
      if (data.status === "game_over") {
        clearInterval(gameInterval);
        alert("Game Over!");
      }
    });
}

function updateBoard(snake, apple) {
  initializeBoard();
  snake.forEach(([x, y]) => {
    document.getElementById(`cell-${x}-${y}`).classList.add("snake");
  });
  const [appleX, appleY] = apple;
  document.getElementById(`cell-${appleX}-${appleY}`).classList.add("apple");
}

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowUp") moveSnake("UP");
  else if (e.key === "ArrowDown") moveSnake("DOWN");
  else if (e.key === "ArrowLeft") moveSnake("LEFT");
  else if (e.key === "ArrowRight") moveSnake("RIGHT");
});

document.getElementById("start-game").onclick = startGame;
