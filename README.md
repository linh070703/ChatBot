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
    -d '{ \
        "message": [ \
            {"user": "Cuong", "content": "Hi, I want to transfer 300k to Minh."} \
        ] \
    }' \
    https://bhdl.jsclub.me/mock/chat
```