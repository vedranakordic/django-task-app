from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import datetime


# Create your models here.
class Task(models.Model):
    title: str = models.CharField(max_length=200)
    description: str = models.TextField(blank=True)
    completed: bool = models.BooleanField(default=False)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    due_date: datetime = models.DateTimeField(null=True, blank=True)

    choices: list[tuple[str, str]] = [
                                        ('urgent', 'Urgent'),     
                                        ('important', 'Important'),  
                                        ('later', 'Later'),       
                                    ]

    priority: str = models.CharField(max_length=20, choices=choices)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)
  
    def __str__(self) -> str:
        return self.title
    