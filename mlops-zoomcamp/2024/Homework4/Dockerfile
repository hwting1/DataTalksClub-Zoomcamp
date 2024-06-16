FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

WORKDIR /app

COPY requirements.txt ./
COPY score.py .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "score.py"]