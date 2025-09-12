from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False)
    email = models.EmailField(unique=True,null=False,blank=False)
    age = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"
