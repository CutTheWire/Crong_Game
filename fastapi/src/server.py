import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from utils.Models import Snake_Response, SnakeMove_Request
from utils.Snake_game import SnakeGame
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

@app.get("/snake", response_class=HTMLResponse)
async def serve_homepage(request: Request, count: int = Query(...)):
    """
    /snake 경로에서 게임 시작 페이지를 반환.
    count 값으로 계산된 키를 저장.
    """
    # 키 생성 로직
    calculated_key = (
        count * 10000 +
        (count + 4.2) * 1000 +
        (count + 1.1) * 100 +
        count * 10 +
        (count % 10)
    )
    salted_key = f"{int(calculated_key)}"

    # 키를 세션에 저장
    request.session['generated_key'] = salted_key

    # 게임 페이지 렌더링
    return templates.TemplateResponse("index.html", {"request": request})

# 게임 데이터 저장소 (임시 메모리 저장)
games = {}

@app.post("/snake/start", response_model=Snake_Response)
def start_game():
    """
    새로운 게임을 시작합니다.
    :return: 새로운 게임의 초기 상태
    """
    game_id = str(uuid.uuid4())
    initial_snake = [(5, 5)]
    apple = SnakeGame.generate_apple(initial_snake)
    game = SnakeGame(game_id=game_id, snake=initial_snake, direction="UP", apple=apple)
    games[game_id] = game
    return Snake_Response(**game.__dict__)

@app.post("/snake/move", response_model=dict)
def move_snake(move_request: SnakeMove_Request, request: Request):
    """
    뱀을 이동시킵니다.
    """
    game_id = move_request.game_id
    direction = move_request.direction

    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    if game.status == "game_over":
        return {"status": "game_over", "snake": game.snake, "apple": game.apple, "score": game.score}

    if direction not in ["UP", "DOWN", "LEFT", "RIGHT"]:
        raise HTTPException(status_code=422, detail=f"Invalid direction: {direction}")

    # 반대 방향으로 이동 방지 (UP <-> DOWN, LEFT <-> RIGHT)
    opposite_directions = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
    if direction == opposite_directions[game.direction]:
        direction = game.direction  # 기존 방향 유지

    # 새로운 방향 업데이트
    game.direction = direction

    # 새로운 머리 위치 계산
    new_head = game.calculate_new_head()

    if game.check_collision(new_head):
        game.status = "game_over"
        return {"status": "game_over", "snake": game.snake, "apple": game.apple, "score": game.score}

    if new_head == game.apple:
        game.snake.insert(0, new_head)  # 길이 증가
        game.apple = SnakeGame.generate_apple(game.snake)
        game.score += 1
    else:
        game.snake.insert(0, new_head)
        game.snake.pop()  # 길이 유지

    # 승리 조건: 스코어가 10 이상일 경우 키 반환
    if game.score >= 10 and game.status != "success":
        game.status = "success"
        generated_key = request.session.get('generated_key', "No key available")
        return {
            "status": "success",
            "key": generated_key,
            "snake": game.snake,
            "apple": game.apple,
            "score": game.score
        }

    # 승리 이후에도 게임 진행
    return {"status": "ongoing", "snake": game.snake, "apple": game.apple, "score": game.score}
