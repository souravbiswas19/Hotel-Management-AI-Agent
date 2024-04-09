FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN python -m venv ./env
RUN apt-get update && apt-get install -y cmake protobuf-compiler libprotobuf-dev
RUN chmod +x ./env/bin/activate
RUN ./env/bin/activate

RUN pip install --no-cache-dir -r requirements.txt
RUN ./env/bin/activate

EXPOSE 8000
