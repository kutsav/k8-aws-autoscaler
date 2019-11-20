FROM python:3.6-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -t . -r requirements.txt

COPY app.py .

CMD ["python3","app.py"]
