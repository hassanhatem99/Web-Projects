from django.contrib.auth.models import AbstractUser
from django.db import models
import os
from django.utils import timezone
from multiupload.fields import MultiImageField

def get_image_path(instance, filename):
    return os.path.join('images', filename)

class User(AbstractUser):
    prof_pic = models.ImageField(upload_to=get_image_path, default="media/images/default.png")
    following = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='followers')

    def follow(self, user):
        """
        Add a user to the following list.
        """
        if not self.follows(user):
            self.following.add(user)
            user.followers.add(self)

    def unfollow(self, user):
        """
        Remove a user from the following list.
        """
        if self.follows(user):
            self.following.remove(user)
            user.followers.remove(self)

    def follows(self, user):
        """
        Check if the user follows the other user.
        """
        return user in self.following.all()
    

class Post(models.Model):      
    caption = models.CharField(max_length=256)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(default=timezone.now())



    def save(self, *args, **kwargs):
        if not self.pk:
            self.time_created = timezone.now()  # Set the current date and time
        super().save(*args, **kwargs)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_image_path)








class LikedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')




class Comment(models.Model):
    text = models.TextField(max_length=500)
    commentor = models.CharField(max_length=64)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    time_created = models.DateTimeField(default=timezone.now())

