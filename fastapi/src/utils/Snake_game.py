import random
from typing import List, Tuple

class SnakeGame:
    """
    게임 상태를 저장하는 데이터 클래스
    """
    def __init__(self, game_id: str, snake: List[Tuple[int, int]], direction: str,
                 apple: Tuple[int, int], score: int = 0, status: str = "ongoing"):
        """
        게임 초기화
        :param game_id: 게임 ID
        :param snake: 뱀의 초기 위치 리스트
        :param direction: 초기 방향 (UP, DOWN, LEFT, RIGHT)
        :param apple: 사과의 초기 위치
        :param score: 초기 점수 (기본값: 0)
        :param status: 게임 상태 (기본값: "ongoing")
        """
        self.game_id = game_id
        self.snake = snake
        self.direction = direction
        self.apple = apple
        self.score = score
        self.status = status

    def calculate_new_head(self) -> Tuple[int, int]:
        """
        새로운 머리 위치를 계산
        :return: 새로운 머리의 좌표
        """
        head_x, head_y = self.snake[0]
        if self.direction == "UP":
            return head_x - 1, head_y
        elif self.direction == "DOWN":
            return head_x + 1, head_y
        elif self.direction == "LEFT":
            return head_x, head_y - 1
        elif self.direction == "RIGHT":
            return head_x, head_y + 1

    def check_collision(self, new_head: Tuple[int, int]) -> bool:
        """
        벽 또는 자신과의 충돌을 확인
        :param new_head: 뱀의 새로운 머리 위치
        :return: 충돌 여부 (True: 충돌)
        """
        x, y = new_head
        if x < 0 or x >= 20 or y < 0 or y >= 20:  # 벽 충돌
            return True
        if new_head in self.snake:  # 자기 자신과 충돌
            return True
        return False

    @staticmethod
    def generate_apple(snake: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        새로운 사과의 위치를 생성
        :param snake: 뱀의 현재 위치
        :return: 생성된 사과의 좌표
        """
        while True:
            apple = (random.randint(0, 19), random.randint(0, 19))
            if apple not in snake:
                return apple
