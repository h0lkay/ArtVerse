from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, PortfolioImage, ArtworkForSale, ArtworkComment


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'social_link']


class PortfolioImageForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['image']


class ArtworkForSaleForm(forms.ModelForm):
    class Meta:
        model = ArtworkForSale
        fields = ['title', 'description', 'price', 'image', 'category']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'price': 'Цена (руб.)',
            'image': 'Изображение',
            'category': 'Категория',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class ArtworkFilterForm(forms.Form):
    title = forms.CharField(label="Название", required=False)
    min_price = forms.DecimalField(label="Мин. цена", required=False, min_value=0)
    max_price = forms.DecimalField(label="Макс. цена", required=False, min_value=0)
    is_sold = forms.ChoiceField(
        label="Статус",
        choices=[('', 'Все'), ('0', 'В продаже'), ('1', 'Продано')],
        required=False
    )
    SORT_CHOICES = [
        ('price_asc', 'Цена (по возрастанию)'),
        ('price_desc', 'Цена (по убыванию)'),
        ('title_asc', 'Название (А-Я)'),
        ('title_desc', 'Название (Я-А)'),
        ('date_asc', 'Дата (сначала старые)'),
        ('date_desc', 'Дата (сначала новые)'),
        ('popular', 'По популярности'),
    ]


class ArtworkCommentForm(forms.ModelForm):
    class Meta:
        model = ArtworkComment
        fields = ['text', 'file']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Напишите комментарий...'}),
        }


class ReportForm(forms.Form):
    REASON_CHOICES = [
        ('adult', 'Неотмеченный контент для взрослых'),
        ('illegal', 'Незаконный контент'),
        ('fraud', 'Мошенничество / Украденное искусство'),
        ('pricing', 'Неверная / вводящая в заблуждение цена'),
        ('attribution', 'Неверное указание авторства при использовании базы'),
        ('other', 'Другое'),
    ]
    reason = forms.ChoiceField(choices=REASON_CHOICES, widget=forms.Select, label="Причина")
    details = forms.CharField(widget=forms.Textarea, required=False, label="Дополнительная информация")
