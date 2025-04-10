from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path, re_path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = "users"

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('password-reset/',
         PasswordResetView.as_view(
             template_name="users/password_reset_form.html",
             email_template_name="users/password_reset_email.html",
             success_url=reverse_lazy("users:password_reset_done")
         ),
         name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name="users/password_reset_confirm.html",
             success_url=reverse_lazy("users:password_reset_complete")
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name='password_reset_complete'),
    path('', views.dashboard, name='dashboard'),
    path('category/<str:category>/', views.dashboard, name='category_filter'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='artist_profile'),
    path('add-artwork/', views.add_artwork, name='add_artwork'),
    path("rules/", views.rules_view, name="platform_rules"),
    path("artwork/<int:artwork_id>/", views.artwork_detail, name="artwork_detail"),
    path("artwork/<int:artwork_id>/edit/", views.edit_artwork, name="edit_artwork"),
    path("artwork/<int:artwork_id>/delete/", views.delete_artwork, name="delete_artwork"),
    path('start_chat/<int:artwork_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/<int:chat_id>/send_message/', views.send_message, name='send_message'),
    path('chats/', views.chat_list, name='chat_list'),
    path("toggle_favorite_artwork/<int:artwork_id>/", views.toggle_favorite_artwork, name="toggle_favorite_artwork"),
    path("toggle_follow_artist/<int:artist_id>/", views.toggle_follow_artist, name="toggle_follow_artist"),
    path("favorite_artworks/", views.favorite_artworks_list, name="favorite_artworks"),
    path("followed_artists/", views.followed_artists, name="followed_artists"),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('check_unread_notifications/', views.check_unread_notifications, name='check_unread_notifications'),
]
