FROM python:3.11-slimq
WORKDIR /appq
COPY . .q
RUN python -m venv ./envq
RUN apt-get update && apt-get install -y cmake protobuf-compiler libprotobuf-devq
RUN chmod +x ./env/bin/activateq
RUN ./env/bin/activateq

RUN pip install --no-cache-dir -r requirements.txtq
RUN ./env/bin/activateq

EXPOSE 8000
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]q