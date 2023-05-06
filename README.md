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

## All features

- [x] I want to transfer 300k to Minh with message "Happy birthday".
    + All possible error case handled
    + I want to transfer money.

- [x] I want to create a chat group with Cuong, Minh, and Tuan.
    + All possible error case handled
    + Tạo group chơi bóng bàn với Linh và Đình Anh

- [x] I want to transfer 200k to everyone in the group.
    + All possible error case handled
    + Chuyển 200k cho mọi người trong group với nội dung "Happy new year"

- [x] I want to transfer 200k to everyone in the group with message "Happy new year".
    + All possible error case handled
    + Chuyển 200k cho mọi người trong group với nội dung "Happy new year"

- [x] Tài khoản của tôi còn bao nhiêu tiền?
  
- [x] Compare Apple, Amazon, and Google.
- [x] General question: VAT là gì?

- [x] Tạo kế hoạch ngân sách hàng tháng.
    - Vì sao mình nên dành từng đó cho các chi tiêu cần thiết?
    - Vì sao mình nên dành từng đó cho tiết kiệm dài hạn
    - Vì sao mình nên dành từng đó cho giáo dục
    - Vì sao mình nên dành từng đó cho hưởng thụ
    - Vì sao mình nên dành từng đó cho tự do tài chính
    - Vì sao mình nên dành từng đó cho từ thiện

- [x] Sau bao lâu thì tôi có thể kiếm được 200 triệu?
- [x] Nếu tôi gửi tiết kiệm sau 20 năm thì tôi có bao nhiêu tiền?
- [x] Tôi muốn đầu tư lướt sóng, bạn có thể tư vấn cho tôi được không?