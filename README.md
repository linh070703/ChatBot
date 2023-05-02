# ChatBot

## 1. Install server
```
bash install_dependencies.sh
```
## 2. Run
```
python3 app.py
```

## API testing

```
curl -X POST -H "Content-Type: application/json" \
    -d '{ "message": [ {"user": "Cuong", "content": "Hi, I want to transfer 300k to Minh."} ] }' \
    http://ai-bhdl.jsclub.me:5001/api/chat
```