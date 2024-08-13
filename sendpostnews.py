import requests
import json

server_url = "http://localhost:8080/news"

news_data = {
    'type': 'news',
    'text': 'Это текст новости, который будет отправлен серверу.'
}

response = requests.post(server_url, json=news_data)

if response.status_code == 200:
    print("Новость успешно отправлена на сервер.")
else:
    print(f"Произошла ошибка при отправке новости: {response.text}")