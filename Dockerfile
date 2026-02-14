FROM python:3.9
WORKDIR /app
# ローカルのファイルをコンテナにコピー
COPY . .
RUN pip install --upgrade pip \
    && pip install uvicorn fastapi \
    && pip install sqlalchemy \
    && pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
