from pydantic import BaseModel, Field
from typing import List, Optional

class Move(BaseModel):
    x: int = Field(..., ge=0, le=9, description="돌의 X 좌표 (0~18)")
    y: int = Field(..., ge=0, le=9, description="돌의 Y 좌표 (0~18)")

class StartGameResponse(BaseModel):
    game_id: str
    board: List[List[str]] = Field(..., description="오목판 상태")

class MoveRequest(BaseModel):
    game_id: str
    user_move: Move

class MoveResponse(BaseModel):
    game_id: str
    board: List[List[str]]
    ai_move: Optional[Move] = None
    result: Optional[str] = Field(None, description="게임 결과 (win/lose/draw/ongoing)")
