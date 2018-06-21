from django.db import models
from apps.auth_facebro.models import User

class Post(models.Model):
    
    content = models.TextField()

    user = models.ForeignKey(User, related_name='user_post', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='following_post', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_comment(self):
        return self.post_comment.all().order_by('created_at')

class Friend(models.Model):

    following = models.ForeignKey(User, related_name='user_following_friend', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_friend', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):

    content = models.CharField(max_length=256)
    
    post = models.ForeignKey(Post, related_name='post_comment', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_comment', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Photo(models.Model):
    
    caption = models.CharField(max_length=128)
    src = models.CharField(max_length=128, unique=True)

    user = models.ForeignKey(User, related_name='user_photo', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)