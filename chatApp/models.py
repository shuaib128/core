import base64
from django.db import models
from users.models import Profile
from django.core.files.base import ContentFile

# Create your models here.
class MediaFile(models.Model):
    filename = models.CharField(max_length=255, default="")
    file = models.FileField(upload_to='media/postsMedia', blank=True)

    #Append chunk method
    def append_chunk(self, chunk_base64):
        # Remove the "data:application/octet-stream;base64," prefix from the Base64 string
        prefix = "data:application/octet-stream;base64,"
        if chunk_base64.startswith(prefix):
            chunk_base64 = chunk_base64[len(prefix):]

        # decode the base64 string into bytes
        chunk = base64.b64decode(chunk_base64)

        if self.file:
            self.file.close()
            self.file.open(mode='ab') # append in binary mode
        else:
            self.file.save(self.filename, ContentFile(b''), save=False)  # Save an empty file
            self.file.close()
            self.file.open(mode='ab')
        self.file.write(chunk)
        self.file.close()
        self.save()

#ChatMessages Model
class ChatMessage(models.Model):
    sender = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    content = models.TextField()
    media_files = models.ManyToManyField(MediaFile, related_name='media', null=True, blank=True)
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