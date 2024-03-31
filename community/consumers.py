from channels.generic.websocket import WebsocketConsumer
import json
from django.contrib.auth.models import User
from .models import ChatBox

class ChatConsumer(WebsocketConsumer):
    rooms = {}

    def connect(self):
        self.sender = self.scope["user"]
        self.receiver_id = self.scope['url_route']['kwargs'].get('receiver_id')
        
        if self.receiver_id:
            try:
                self.receiver = User.objects.get(id=self.receiver_id)
            except User.DoesNotExist:
                self.close()
            self.room_name = self.get_or_create_room_name()
        else:
            self.room_name = self.scope['url_route']['kwargs'].get('group_name')
            self.group_name = f"chat_{self.room_name}"
            self.channel_layer.group_add(self.group_name, self.channel_name)
        
        self.accept()

    def disconnect(self, close_code):
        if not self.receiver_id:
            self.channel_layer.group_discard(self.group_name, self.channel_name)
        else:
            self.rooms.pop(self.room_name, None)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        
        if self.receiver_id:
            # Individual messaging
            message = ChatBox.objects.create(sender=self.sender, receiver=self.receiver_id, message=message_content)
            self.send_message(message, self.sender)
        else:
            # Group messaging
            self.send_message(message, self.sender, is_group=True)

    def get_or_create_room_name(self):
        if self.sender.id > self.receiver.id:
            room_name = f"chat_{self.receiver.id}_{self.sender.id}"
        else:
            room_name = f"chat_{self.sender.id}_{self.receiver.id}"

        if room_name not in self.rooms:
            self.rooms[room_name] = room_name
        
        return room_name

    def send_message(self, message_object, sender_object, is_group=False):

        sender_data = {
            'id': sender_object.id,
            'username': sender_object.username,  # Add other fields as needed
        }

        message_data = {
            'id': message_object.id,
            'message': message_object.message,
        }

        if is_group:
            # Send message to group
            self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.message',
                    'message': message_data,
                    'sender': sender_data
                }
            )
        else:
            # Send message to individual
            self.send(text_data=json.dumps({
                'message': message_data,
                'sender': sender_data
            }))

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
