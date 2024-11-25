import os
import yaml
import uuid
import uvicorn
import asyncio
from dotenv import load_dotenv
from asyncio import TimeoutError
from typing import List, Tuple
from pydantic import ValidationError, BaseModel
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Request)
from starlette.responses import JSONResponse, StreamingResponse
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from utils.Models import StartGameResponse, MoveRequest, MoveResponse, Move
import utils.Error_handlers as ChatError

load_dotenv()

app = FastAPI()
ChatError.add_exception_handlers(app)  # 예외 핸들러 추가

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # 예외를 안전하게 처리
            return await ChatError.generic_exception_handler(request, e)


app.add_middleware(ExceptionMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_KEY", "default-secret")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Crong_Game",
        version="v1.0.0",
        summary="Crong_Game API",
        routes=app.routes,
        description=(
            "이 API는 다음과 같은 기능을 제공합니다:\n\n"
            "각 엔드포인트의 자세한 정보는 해당 엔드포인트의 문서에서 확인할 수 있습니다."
        ),
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://drive.google.com/thumbnail?id=12PqUS6bj4eAO_fLDaWQmoq94-771xfim"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Static 및 Templates 경로 설정
app.mount("/static", StaticFiles(directory="/app/src/static"), name="static")
templates = Jinja2Templates(directory="/app/src/templates")

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """
    기본 HTML 페이지 제공
    """
    return templates.TemplateResponse("index.html", {"request": request})

# 게임 데이터 저장소 (임시 메모리 저장)

# 게임 상태 저장
games = {}

class SnakeGame(BaseModel):
    game_id: str
    snake: List[Tuple[int, int]]
    direction: str
    apple: Tuple[int, int]
    score: int
    status: str  # "ongoing", "game_over"

@app.post("/snake/start", response_model=SnakeGame)
def start_game():
    """
    지렁이 게임 시작
    """
    game_id = str(uuid.uuid4())
    initial_snake = [(5, 5)]
    apple = generate_apple(initial_snake)
    games[game_id] = {
        "snake": initial_snake,
        "direction": "UP",
        "apple": apple,
        "score": 0,
        "status": "ongoing"
    }
    return {"game_id": game_id, **games[game_id]}

@app.post("/snake/move", response_model=SnakeGame)
def move_snake(game_id: str, direction: str):
    """
    지렁이 이동
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]
    if game["status"] == "game_over":
        return game

    # 방향 업데이트
    if direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
        game["direction"] = direction

    # 새로운 머리 위치 계산
    new_head = calculate_new_head(game["snake"], game["direction"])

    # 충돌 확인
    if check_collision(new_head, game["snake"]):
        game["status"] = "game_over"
        return game

    # 사과 먹기
    if new_head == game["apple"]:
        game["snake"].insert(0, new_head)  # 길이 증가
        game["apple"] = generate_apple(game["snake"])
        game["score"] += 1
    else:
        game["snake"].insert(0, new_head)
        game["snake"].pop()  # 길이 유지

    return game

def calculate_new_head(snake: List[Tuple[int, int]], direction: str) -> Tuple[int, int]:
    head_x, head_y = snake[0]
    if direction == "UP":
        return head_x - 1, head_y
    elif direction == "DOWN":
        return head_x + 1, head_y
    elif direction == "LEFT":
        return head_x, head_y - 1
    elif direction == "RIGHT":
        return head_x, head_y + 1

def check_collision(new_head: Tuple[int, int], snake: List[Tuple[int, int]]) -> bool:
    """
    벽 또는 자신과의 충돌 확인
    """
    x, y = new_head
    if x < 0 or x >= 20 or y < 0 or y >= 20:  # 벽 충돌
        return True
    if new_head in snake:  # 자기 자신과 충돌
        return True
    return False

def generate_apple(snake: List[Tuple[int, int]]) -> Tuple[int, int]:
    """
    새로운 사과 생성
    """
    while True:
        apple = (random.randint(0, 19), random.randint(0, 19))
        if apple not in snake:
            return apple