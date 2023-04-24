FROM python3

RUN mkdir -p /app
WORKDIR /app
COPY app.py /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

CMD waitress-serve --host 0.0.0.0 --port 5000 app:app 