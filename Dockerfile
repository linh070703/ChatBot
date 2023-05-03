FROM python:3.9

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY src /app/src
COPY app.py /app

# CMD waitress-serve --host 0.0.0.0 --port 5000 app:app 
CMD flask run --host 0.0.0.0 --port 5000