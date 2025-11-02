# thrift-market


cd ~/thrift-market/backend \
pip install -r requirements.txt \
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

**

curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok

  **

  ngrok config add-authtoken 30oOnZa6unxi8on6V44IyadpvOV_5jfZeUkJ8kLbQZHKJP2gH

  **

  ngrok http 8000

#check

curl -X POST http://localhost:8000/api/order/create -H "Content-Type: application/json" -d '{"buyer_id": 2, "product_id": 2}'
\
curl -X PUT http://localhost:8000/api/order/confirm -H "Content-Type: application/json" -d '{"order_id": 2, "seller_id": 1}'
\
curl -X PUT http://localhost:8000/api/order/finish -H "Content-Type: application/json" -d '{"order_id": 2, "by_user_id": 2}'
\
curl -X PUT http://localhost:8000/api/order/cancel -H "Content-Type: application/json" -d '{"order_id": 1, "by_user_id": 1}'
