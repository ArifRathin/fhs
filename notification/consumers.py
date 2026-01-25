import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):


    async def connect(self):
        self.group_name = f"user__{self.scope['user'].id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print("Accepted!")


    async def send_notification(self, event):
        print(event["message"])
        await self.send(text_data=json.dumps(event["message"]))