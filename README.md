# ChatBot

## 1. Install server
```
bash install_dependencies.sh
```
## 2. Run
```
python3 app.py
```

## 3. Test
```
curl -X POST -H "Content-Type: application/json" -d '{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Who won the world series in 2020?"}, {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."}, {"role": "user", "content": "Where was it played?"}]}' http://localhost:5000/api/chat
```
