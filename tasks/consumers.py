import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Start heartbeat
        self.keep_alive_task = asyncio.create_task(self.keep_alive())

        # Broadcast that a user joined (Presence)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence_update',
                'message': f'Someone joined the chat.',
                'status': 'online'
            }
        )

    async def keep_alive(self):
        try:
            while True:
                await asyncio.sleep(2)
                await self.send(text_data=json.dumps({'type': 'ping'}))
        except asyncio.CancelledError:
            pass

    async def disconnect(self, close_code):
        if hasattr(self, 'keep_alive_task'):
            self.keep_alive_task.cancel()
            
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Broadcast that a user left (Presence)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence_update',
                'message': f'Someone left the chat.',
                'status': 'offline'
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        sender = data.get('sender', 'Anonymous')

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'sender': event['sender'],
        }))
        
    # New handler for presence updates
    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'message': event['message'],
            'status': event['status']
        }))