FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY nba_champion_model.pkl /app/nba_champion_model.pkl

CMD ["python", "app/app.py"]
ENV PYTHONUNBUFFERED=1
