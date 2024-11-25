# Step 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# 필요한 파일 복사 및 설치
COPY requirements.txt .
COPY ./src /app/src
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt

# Step 2: Final stage
FROM python:3.11-slim

WORKDIR /app

# 빌드 단계에서 생성한 venv를 복사
COPY --from=builder /app/venv /app/venv
COPY ./src /app/src

# 환경 변수 설정
ENV VIRTUAL_ENV=/app/venv
ENV PATH="/app/venv/bin:$PATH"

# 어플리케이션 실행
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
