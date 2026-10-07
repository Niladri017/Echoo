import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Conversation, Message
from django.utils.timezone import localtime


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        conversation = await self.get_conversation()

        if conversation is None:
            await self.close()
            return

        if not await self.is_participant(conversation):
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_conversation(self):
        return Conversation.objects.filter(
            id=self.room_name
        ).first()

    @database_sync_to_async
    def is_participant(self, conversation):
        return conversation.participants.filter(
            id=self.scope["user"].id
        ).exists()

    @database_sync_to_async
    def save_message(self, message_text):
        conversation = Conversation.objects.get(
            id=self.room_name
        )

        message = Message.objects.create(
            conversation=conversation,
            sender=self.scope["user"],
            text=message_text
        )

        return message

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        saved_message = await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.scope["user"].username,
                "created_at": localtime(saved_message.created_at).strftime("%H:%M"),
            }
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps({
                "message": event["message"],
                "sender": event["sender"],
                "created_at": event["created_at"],
            })
        )