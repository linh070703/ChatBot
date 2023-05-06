# ChatBot

## 1. Install server

```bash
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

## 2. Run

```bash
flask run --host 0.0.0.0 --port 5000
```

## Run with docker

```bash
docker compose up  # that's all
```

## API testing

```bash
curl -i -X POST -H "Content-Type: application/json" \
    -d '{ "messages": [ {"user": "Cuong", "content": "Hi, I want to transfer 300k to Minh."} ] }' \
    https://ai-bhdl.jsclub.me/api/chat
```

```bash
curl -i -X POST -H "Content-Type: application/json" \
    -d '{ "messages": [ {"user": "Cuong", "content": "Hi, I want to transfer 300k to Minh."} ] }' \
    http://localhost:5000/api/chat
```