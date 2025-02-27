from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import UserProfile, PortfolioImage
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, PortfolioImageForm


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
    return render(request, 'users/dashboard.html', {'section': 'dashboard'})


@login_required
def profile(request):
    user_profile = request.user.profile
    portfolio_images = PortfolioImage.objects.filter(user=request.user)

    if request.method == 'POST':
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
        'form': form
    })

