FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

RUN apt update && apt-get install -y apt-utils 2>&1

WORKDIR .
COPY . .

RUN pip install -r requirements.txt

# start serving
CMD python3 serve.py
