FROM python:3.11.7-slim
RUN apt update && apt -y -q install curl
COPY src/server.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD python3 server.py