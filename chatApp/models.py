from django.db import models
from users.models import Profile

# Create your models here.
class ChatImage(models.Model):
    name = models.CharField(max_length=10000, default="Image Name")
    image = models.ImageField(null=True, blank=True, upload_to="media/chatImages")

class ChatVideo(models.Model):
    name = models.CharField(max_length=10000, default="Video Name")
    video = models.FileField(null=True, blank=True, upload_to="media/chatVideos")

#ChatMessages Model
class ChatMessage(models.Model):
    sender = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    content = models.TextField()
    images = models.ManyToManyField(ChatImage, related_name="Images", null=True, blank=True)
    videos = models.ManyToManyField(ChatVideo, related_name="videos", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} : {self.content}'
    
#Chatroom Model
class ChatRoom(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(Profile, related_name='member', swappable=True)
    chatContext = models.ManyToManyField(
        ChatMessage, related_name="ChatContent", null=True,blank=True
    )

    def __str__(self):
        return self.name+str(self.id)