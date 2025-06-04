FROM python:3.11-slim

WORKDIR /workdir 

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src .

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0"]