FROM python:3.11-slim

WORKDIR /workdir 

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

CMD [ "python3", "./src/main.py"]