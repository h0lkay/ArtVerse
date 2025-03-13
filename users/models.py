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


class ArtworkForSale(models.Model):
    CATEGORY_CHOICES = [
        ('Популярное', 'Популярное'),
        ('Природа', 'Природа'),
        ('Абстракция', 'Абстракция'),
        ('Аниме', 'Аниме'),
        ('Оригинальные персонажи', 'Оригинальные персонажи'),
        ('Фан-Арт', 'Фан-Арт'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artworks_for_sale')
    image = models.ImageField(upload_to='artworks/')
    title = models.CharField(max_length=255, verbose_name="Название работы")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='featured', verbose_name="Категория")
    is_sold = models.BooleanField(default=False, verbose_name="Продано")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.title}'

