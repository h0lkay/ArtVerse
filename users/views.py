from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, PortfolioImage, ArtworkForSale, PlatformRules, Chat, Message, FavoriteArtworks, \
    FollowedArtist, Notification, ArtworkVote, ArtworkComment, CommentLike
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm, PortfolioImageForm, \
    ArtworkForSaleForm, ArtworkFilterForm, ArtworkCommentForm
from django.http import HttpResponse, Http404
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import os
from io import BytesIO
import json
from .forms import ReportForm
from .models import Report

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен')
        else:
            messages.error(request, 'Ошибка в обновлении профиля')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'users/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            profile = UserProfile.objects.create(user=new_user)
            return render(request, 'users/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'users/register.html', {'user_form': user_form})


def dashboard(request):
    selected_category = request.GET.get('category')
    categories = [('Все', 'Все')] + list(ArtworkForSale.CATEGORY_CHOICES)
    if selected_category and selected_category != 'Все':
        artworks = ArtworkForSale.objects.filter(category=selected_category)
    else:
        artworks = ArtworkForSale.objects.all()

    form = ArtworkFilterForm(request.GET)
    if form.is_valid():
        title = form.cleaned_data.get('title')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        is_sold = form.cleaned_data.get('is_sold')
        sort_by = request.GET.get('sort_by')

        if title:
            artworks = artworks.filter(title__icontains=title)
        if min_price is not None:
            artworks = artworks.filter(price__gte=min_price)
        if max_price is not None:
            artworks = artworks.filter(price__lte=max_price)
        if is_sold in ['0', '1']:
            artworks = artworks.filter(is_sold=bool(int(is_sold)))
        if sort_by == 'price_asc':
            artworks = artworks.order_by('price')
        elif sort_by == 'price_desc':
            artworks = artworks.order_by('-price')
        elif sort_by == 'title_asc':
            artworks = artworks.order_by('title')
        elif sort_by == 'title_desc':
            artworks = artworks.order_by('-title')
        elif sort_by == 'date_asc':
            artworks = artworks.order_by('uploaded_at')
        elif sort_by == 'date_desc':
            artworks = artworks.order_by('-uploaded_at')
        elif sort_by == 'popular':
            artworks = sorted(artworks, key=lambda a: a.likes_count - a.dislikes_count, reverse=True)
        else:
            # Сортировка по умолчанию, если не выбрана другая
            artworks = artworks.order_by('-uploaded_at')
    return render(request, 'users/dashboard.html', {'artworks': artworks, 'categories': categories,
                                                    'selected_category': selected_category,
                                                    'form': form,
                                                    'sort_choices': ArtworkFilterForm.SORT_CHOICES})


@login_required
def profile(request, username=None):
    # Если username не передан, используем текущего пользователя
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    # Получаем профиль пользователя
    user_profile = get_object_or_404(UserProfile, user=user)
    # Получаем работы пользователя
    portfolio_images = PortfolioImage.objects.filter(user=user)

    # Если это текущий пользователь, разрешаем добавлять работы
    if user == request.user and request.method == 'POST':
        form = PortfolioImageForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio_image = form.save(commit=False)
            portfolio_image.user = request.user
            portfolio_image.save()
            return redirect('users:profile')
    else:
        form = PortfolioImageForm()

    return render(request, 'users/profile.html', {
        'user_profile': user_profile,
        'portfolio_images': portfolio_images,
        'form': form if user == request.user else None,  # Форма только для текущего пользователя
        'is_current_user': user == request.user,  # Флаг, чтобы проверить, это текущий пользователь или нет
    })


@login_required
def add_artwork(request):
    if request.method == 'POST':
        form = ArtworkForSaleForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.user = request.user
            artwork.save()
            return redirect('users:dashboard')
    else:
        form = ArtworkForSaleForm()

    return render(request, 'users/add_artwork.html', {'form': form})


def rules_view(request):
    rules = PlatformRules.objects.all()
    return render(request, "users/platform_rules.html", {"rules": rules})


def artwork_detail(request, artwork_id):
    artwork = get_object_or_404(ArtworkForSale, id=artwork_id)

    comments = artwork.comments.filter(parent__isnull=True)

    if request.method == 'POST':
        form = ArtworkCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.artwork = artwork

            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = ArtworkComment.objects.get(id=parent_id)

            comment.save()
            return redirect('users:artwork_detail', artwork_id=artwork.id)
    else:
        form = ArtworkCommentForm()

    context = {
        'artwork': artwork,
        'comments': comments,
        'comment_form': form,
    }
    return render(request, 'users/artwork_detail.html', context)


@login_required
def start_chat(request, artwork_id):
    """Создать или перейти к чату с художником."""
    artwork = get_object_or_404(ArtworkForSale, id=artwork_id)
    customer = request.user
    artist = artwork.user

    # Проверяем, существует ли уже чат
    chat = Chat.objects.filter(order=artwork, customer=customer, artist=artist).first()

    if not chat:
        # Создаем новый чат
        chat = Chat.objects.create(order=artwork, customer=customer, artist=artist)

    # Перенаправляем на страницу чата
    return redirect('users:chat_detail', chat_id=chat.id)


@login_required
def chat_detail(request, chat_id):
    """Отображение чата и сообщений."""
    chat = get_object_or_404(Chat, id=chat_id)
    chat_messages = chat.messages.all().order_by('created_at')

    # Проверка, что пользователь имеет доступ к чату
    if request.user != chat.customer and request.user != chat.artist:
        return redirect('home')

    return render(request, 'users/chat_detail.html', {
        'chat': chat,
        'chat_messages': chat_messages,
    })


@login_required
def send_message(request, chat_id):
    """Отправка сообщения в чат."""
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id)
        text = request.POST.get('text', '').strip()

        if text:
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text,
            )

            # Определяем получателя сообщения (того, кто не является отправителем)
            recipient = chat.customer if request.user == chat.artist else chat.artist

            # Отправляем уведомление только получателю
            send_message_notification(recipient, message.text, request.user.username)

            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Сообщение не может быть пустым'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Недопустимый метод запроса'}, status=405)


@login_required
def chat_list(request):
    """Отображение списка чатов для текущего пользователя."""
    # Получаем все чаты, где текущий пользователь является заказчиком или художником
    chats = Chat.objects.filter(customer=request.user) | Chat.objects.filter(artist=request.user)
    chats = chats.order_by('-created_at')  # Сортировка по дате создания (новые сверху)

    return render(request, 'users/chat_list.html', {'chats': chats})


@login_required
def edit_artwork(request, artwork_id):
    artwork = get_object_or_404(ArtworkForSale, id=artwork_id, user=request.user)

    if request.method == "POST":
        form = ArtworkForSaleForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            form.save()
            return redirect("users:artwork_detail", artwork_id=artwork.id)
    else:
        form = ArtworkForSaleForm(instance=artwork)

    return render(request, "users/edit_artwork.html", {"form": form, "artwork": artwork})


@login_required
def delete_artwork(request, artwork_id):
    artwork = get_object_or_404(ArtworkForSale, id=artwork_id, user=request.user)

    if request.method == "POST":
        artwork.delete()
        return redirect("users:dashboard")  # Перенаправление на страницу профиля после удаления


@login_required
def toggle_favorite_artwork(request, artwork_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        artwork = ArtworkForSale.objects.get(id=artwork_id)
    except ArtworkForSale.DoesNotExist:
        return JsonResponse({"error": "Artwork not found"}, status=404)

    favorite, created = FavoriteArtworks.objects.get_or_create(user=request.user, artwork=artwork)

    if not created:
        favorite.delete()
        return JsonResponse({"status": "removed"})  # Удалено из избранного
    else:
        send_favorite_notification(artwork, request.user)  # Отправка уведомления
        return JsonResponse({"status": "added"})  # Добавлено в избранное


@login_required
def toggle_follow_artist(request, artist_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"error": "Invalid request"}, status=400)

    artist = get_object_or_404(User, id=artist_id)

    if artist == request.user:
        return JsonResponse({"error": "Cannot follow yourself"}, status=400)

    follow, created = FollowedArtist.objects.get_or_create(
        follower=request.user,
        artist=artist
    )

    if not created:
        follow.delete()
        return JsonResponse({"status": "unfollowed"})
    else:
        send_follow_notification(artist, request.user)
        return JsonResponse({"status": "followed"})


@login_required
def favorite_artworks_list(request):
    favorite_artworks = FavoriteArtworks.objects.filter(user=request.user).select_related("artwork")
    return render(request, "users/favorite_artworks.html", {"favorite_artworks": favorite_artworks})


@login_required
def followed_artists(request):
    followed = FollowedArtist.objects.filter(follower=request.user).select_related('artist__profile')
    followed_with_ratings = [
        {
            'artist': follow.artist,
            'profile': follow.artist.profile,
        }
        for follow in followed
    ]
    return render(request, 'users/followed_artists.html', {
        'followed_artists': followed_with_ratings
    })


@login_required
def notifications(request):
    # Получаем все уведомления для текущего пользователя, сортируем по дате
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'users/notifications.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notification_id):
    # Получаем уведомление по ID и помечаем его как прочитанное
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('users:notifications')


def send_message_notification(recipient, message_text, sender_username):
    # Создаем уведомление о новом сообщении
    Notification.objects.create(
        user=recipient,
        message=f'Новое сообщение от {sender_username}: {message_text}',
        notification_type='message',
    )


def send_follow_notification(artist, follower):
    # Уведомление о новом подписчике
    Notification.objects.create(
        user=artist,
        message=f'{follower.username} подписался на вас!',
        notification_type='follow',
    )


def send_favorite_notification(artwork, user):
    # Уведомление о добавлении работы в избранное
    Notification.objects.create(
        user=artwork.user,
        message=f'Ваша работа "{artwork.title}" была добавлена в избранное!',
        notification_type='favorite',
    )


@login_required
def check_unread_notifications(request):
    # Получаем первые 5 непрочитанных уведомлений
    unread_notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]

    # Формируем список уведомлений
    notifications_data = [
        {
            'id': notification.id,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
            'type': notification.notification_type
        }
        for notification in unread_notifications
    ]

    return JsonResponse({
        'unread_count': request.user.notifications.filter(is_read=False).count(),
        'notifications': notifications_data
    })


def watermarked_image_view(request, artwork_id):
    artwork = get_object_or_404(ArtworkForSale, id=artwork_id)

    if not artwork.image:
        raise Http404("Изображение не найдено")

    image_path = os.path.join(settings.MEDIA_ROOT, artwork.image.name)
    if not os.path.exists(image_path):
        raise Http404("Файл изображения не существует")

    with Image.open(image_path).convert("RGBA") as base:
        watermark = Image.new("RGBA", base.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)

        text = "ArtVerse"
        font_size = int(min(base.size) / 15)

        try:
            font_path = os.path.join(settings.BASE_DIR, "arial.ttf")
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        # Создание одного слоя текста, повернутого по диагонали
        text_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_layer)

        spacing_x = font_size * 4
        spacing_y = font_size * 4

        for y in range(0, base.size[1] + spacing_y, spacing_y):
            for x in range(0, base.size[0] + spacing_x, spacing_x):
                text_draw.text((x, y), text, font=font, fill=(255, 255, 255, 80))

        # Поворот слоя с текстом
        rotated_text = text_layer.rotate(-30, expand=1)

        # Центрируем повёрнутый слой на изображении
        watermark.paste(rotated_text, (
            (base.size[0] - rotated_text.size[0]) // 2,
            (base.size[1] - rotated_text.size[1]) // 2
        ), rotated_text)

        # Объединяем изображение с водяным знаком
        combined = Image.alpha_composite(base, watermark)

        output = BytesIO()
        combined.convert("RGB").save(output, "JPEG", quality=90)
        output.seek(0)

        return HttpResponse(output.read(), content_type="image/jpeg")


@require_POST
@login_required
def like_comment(request, comment_id):
    try:
        comment = ArtworkComment.objects.get(id=comment_id)
        user = request.user

        if user in comment.likes.all():
            comment.likes.remove(user)
            status = 'unliked'
        else:
            comment.likes.add(user)
            status = 'liked'

        return JsonResponse({
            'status': status,
            'total_likes': comment.likes.count()
        })
    except ArtworkComment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Комментарий не найден'}, status=404)


@require_POST
def vote_artwork(request, artwork_id):
    artwork = get_object_or_404(ArtworkForSale, id=artwork_id)
    data = json.loads(request.body)
    value = data.get("value")

    vote, created = ArtworkVote.objects.update_or_create(
        user=request.user,
        artwork=artwork,
        defaults={'value': value}
    )

    return JsonResponse({
        "likes": artwork.likes_count,
        "dislikes": artwork.dislikes_count,
    })


@login_required
def report_user(request, user_id):
    reported_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            Report.objects.create(
                reporter=request.user,
                reported=reported_user,
                reason=form.cleaned_data['reason'],
                details=form.cleaned_data['details']
            )
            return redirect('users:dashboard')
    else:
        form = ReportForm()
    return render(request, 'users/report_form.html', {'form': form, 'reported_user': reported_user})
