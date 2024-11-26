from pydantic import BaseModel
from typing import List, Tuple

class Snake_Response(BaseModel):
    game_id: str
    snake: List[Tuple[int, int]]
    direction: str
    apple: Tuple[int, int]
    score: int
    status: str  # "ongoing", "game_over"
    
class SnakeMove_Request(BaseModel):
    game_id: str
    direction: str