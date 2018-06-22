from django.db import models

class User(models.Model):
    
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_avatar(self):
        return self.user_profile.get(is_active=1)

class Profile(models.Model):
    
    image = models.CharField(max_length=64, null=True)
    is_active = models.IntegerField()

    user = models.ForeignKey(User, related_name='user_profile', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)