from django.db import models
from django.contrib.auth.models import User
from hub.models import Car
# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']  # show messages in order

    def __str__(self):
        return f"{self.sender} to {self.receiver} ({self.car.name})"