from django.db import models

# Create your models here.
class ChatHistory(models.Model):
    id =models.CharField(primary_key=True)
    user_email = models.CharField(max_length=256)
    file_key= models.CharField(max_length=512)
    response = models.TextField()
    timestamp = models.DateTimeField()
    sources_links= models.JSONField(default=list) 
    def __str__(self):
        return f"{self.id}-> {self.user_email}"
