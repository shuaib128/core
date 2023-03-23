from django.db import models
from users.models import Profile

# Create your models here.
class ChatMessage(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} : {self.content}'
    
class ChatRoom(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(Profile, related_name='member')
    chatContext = models.ManyToManyField(
        ChatMessage, related_name="ChatContent", null=True,blank=True
    )

    def __str__(self):
        return self.name+str(self.id)