FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./start.sh ./celery_worker.sh ./celery_beat.sh


RUN useradd -m -s /bin/bash carappuser && chown -R carappuser:carappuser /app

USER carappuser

EXPOSE 8000

CMD ["./start.sh"]
