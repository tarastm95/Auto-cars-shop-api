from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from django.contrib.auth.models import User
import logging

class TestDriveConsumer(AsyncAPIConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_authenticated:
            try:
                self.other_user = self.scope['url_route']['kwargs']['other_user']
                chat_group_name = self.get_chat_group_name(user.username, self.other_user)
                await self.channel_layer.group_add(chat_group_name, self.channel_name)
                await self.accept()
                await self.send_json({'message': f'Welcome to the chat, {user.username} and {self.other_user}!'})
            except KeyError:
                await self.close(code=400)
            except Exception:
                await self.close(code=500)
        else:
            await self.close(code=403)

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            try:
                chat_group_name = self.get_chat_group_name(user.username, self.other_user)
                await self.channel_layer.group_discard(chat_group_name, self.channel_name)
            except Exception:
                pass

    async def receive_json(self, content):
        user = self.scope['user']
        try:
            recipient = content.get('recipient')
            message = content.get('message')
            if recipient and message:
                chat_group_name = self.get_chat_group_name(user.username, recipient)
                await self.channel_layer.group_send(
                    chat_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender": user.username,
                    }
                )
        except KeyError:
            pass
        except Exception:
            pass

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send_json({
            'message': message,
            'sender': sender
        })

    def get_chat_group_name(self, user1, user2):
        group_name = f"chat_{min(user1, user2)}_{max(user1, user2)}"
        return group_name
