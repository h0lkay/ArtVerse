from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import UserProfile, PortfolioImage, ArtworkForSale
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, PortfolioImageForm, \
    ArtworkForSaleForm, ArtworkFilterForm


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
        else:
            # Сортировка по умолчанию, если не выбрана другая
            artworks = artworks.order_by('-uploaded_at')
    return render(request, 'users/dashboard.html', {'artworks': artworks, 'categories': categories,
                                                    'selected_category': selected_category,
                                                    'form': form,
                                                    'sort_choices': ArtworkFilterForm.SORT_CHOICES})


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
