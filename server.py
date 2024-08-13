import aiohttp
import json
from aiohttp import web

class ChatServer:
    def __init__(self):
        self.websockets = []
        self.users = []

    async def register(self, ws, username):
        if username in self.users: # если имя занято - высылаем ошибку и закрываем соединение!
            await ws.send_str(json.dumps({'type': 'loginerror', 'message': 'Username is already taken.'}))
            await ws.close()
            return False
        else: # если имя свободно, добавляем в списки и высылаем ему сообщение что он удачно вошел
            self.websockets.append(ws)
            self.users.append(username)
            await ws.send_str(json.dumps({'type': 'loginsuccess', 'message': 'Good'}))
            print(f'Пользователь {username} подключился.')
            print(self.users)
            return True

    async def unregister(self, ws, username=None):
        self.websockets.remove(ws)
        if username is not None and username in self.users:
            self.users.remove(username)
            print(f'Пользователь {username} вышел.')

    async def send_message(self, message):
        for ws in self.websockets:
            await ws.send_str(message)

    async def ws_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        username = None
        try:
            async for msg in ws:
                print(msg)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = msg.json()
                    if data['type'] == 'message':
                        await self.send_message(msg.data)
                    elif data['type'] == 'ping':
                        await ws.send_str(json.dumps({'type': 'pong', 'message': 'ok'}))
                    elif data['type'] == 'login':
                        username = data['data']['username']
                        if not await self.register(ws, username): # если регистрация не прошла - закрываем генератор ws 
                            break
                        else:
                            await self.send_message(json.dumps({'type': 'newuser', 'username': username})) # оповещаем всех пользователей что зашел новый юзер
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('ws connection closed with exception %s' % ws.exception())
        finally:
            await self.unregister(ws, username)
        return ws
    async def send_news(self, request):
        # Получаем данные из POST-запроса
        data = await request.json()
        if data.get('type') == 'news':
            news_text = data.get('text','Новость какая-то')
            # Рассылаем новости подключенным пользователям
            await self.send_message(json.dumps({'type': 'news', 'text': news_text}))
            return web.Response(text="Новость отправлена всем пользователям")
        else:
            return web.Response(text="Принимается только POST запрос с type:'news'", status=400)
        
app = web.Application()
chat_server = ChatServer()
app.add_routes([
    web.get('/', chat_server.ws_handler),
    web.post('/news', chat_server.send_news)
])
web.run_app(app, port=8080)