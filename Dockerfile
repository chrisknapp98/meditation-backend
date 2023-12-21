FROM python:3.11.7-slim
RUN apt update && apt -y -q install curl
WORKDIR /app
COPY src src
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD python3 src/server.py