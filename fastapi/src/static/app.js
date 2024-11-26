const boardSize = 20;
let gameId = null;
let gameInterval = null;
let currentDirection = "UP";
let totalCells = boardSize * boardSize;

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
  document.getElementById("success-message").classList.add("hidden");
  document.getElementById("success-message").innerText = "";
  document.getElementById("final-message").classList.add("hidden");
  document.getElementById("final-message").innerText = "";
  fetch("/snake/start", { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      gameId = data.game_id;
      currentDirection = data.direction;
      updateBoard(data.snake, data.apple);
      document.getElementById("score").innerText = `Score: ${data.score}`;
      if (gameInterval) clearInterval(gameInterval);
      gameInterval = setInterval(() => moveSnake(currentDirection), 350); // 이동 속도
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
      if (data.snake.length >= totalCells) {
        // 게임이 맵 전체를 채운 경우
        clearInterval(gameInterval);
        document.getElementById("final-message").innerText = `축하합니다!`;
        document.getElementById("final-message").classList.remove("hidden");
        return;
      }

      if (data.status === "success") {
        // 스코어가 10 이상일 경우 성공 메시지 표시
        const key = data.key || "No key available";
        document.getElementById("success-message").innerText = `성공 키 : ${key}`;
        document.getElementById("success-message").classList.remove("hidden");
      }

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

// 키보드 방향키로 방향 설정
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowUp" && currentDirection !== "DOWN") {
    currentDirection = "UP";
  } else if (e.key === "ArrowDown" && currentDirection !== "UP") {
    currentDirection = "DOWN";
  } else if (e.key === "ArrowLeft" && currentDirection !== "RIGHT") {
    currentDirection = "LEFT";
  } else if (e.key === "ArrowRight" && currentDirection !== "LEFT") {
    currentDirection = "RIGHT";
  }
});

// 방향 버튼 클릭으로 방향 설정
document.getElementById("btn-up").onclick = () => {
  if (currentDirection !== "DOWN") currentDirection = "UP";
};
document.getElementById("btn-down").onclick = () => {
  if (currentDirection !== "UP") currentDirection = "DOWN";
};
document.getElementById("btn-left").onclick = () => {
  if (currentDirection !== "RIGHT") currentDirection = "LEFT";
};
document.getElementById("btn-right").onclick = () => {
  if (currentDirection !== "LEFT") currentDirection = "RIGHT";
};

document.getElementById("start-game").onclick = startGame;

// 테마 변경 버튼
document.getElementById("dark-mode").onclick = () => {
  document.body.classList.add("dark-mode");
};
document.getElementById("light-mode").onclick = () => {
  document.body.classList.remove("dark-mode");
};
