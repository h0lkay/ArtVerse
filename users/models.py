from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(verbose_name="О себе", blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    social_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)


class PortfolioImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio')
    image = models.ImageField(upload_to='portfolio/')
    title = models.CharField(max_length=255, blank=True, verbose_name="Название работы")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.title if self.title else "Artwork"}'
