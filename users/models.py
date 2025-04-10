from django.utils import timezone

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


class PlatformRules(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст правил")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Правило платформы"
        verbose_name_plural = "Правила платформы"

    def __str__(self):
        return self.title


class Chat(models.Model):
    """Модель для хранения чата между заказчиком и художником."""
    order = models.ForeignKey(ArtworkForSale, on_delete=models.CASCADE, related_name='chats')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_chats')
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artist_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Чат по заказу {self.order.title}"


class Message(models.Model):
    """Модель для хранения сообщений в чате."""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.sender.username} в чате {self.chat.id}"


class FavoriteArtworks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_artworks")
    artwork = models.ForeignKey(ArtworkForSale, on_delete=models.CASCADE, related_name="favorited_by")

    class Meta:
        unique_together = ("user", "artwork")

    def __str__(self):
        return f"{self.user.username} - {self.artwork.title}"


class FollowedArtist(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'artist')

    def __str__(self):
        return f"{self.follower.username} подписан на {self.artist.username}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('message', 'Новое сообщение'),
        ('follow', 'Новый подписчик'),
        ('favorite', 'Работа добавлена в избранное'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='message')
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
