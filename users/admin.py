from django.contrib import admin

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'avatar']


admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(ArtworkForSale)
admin.site.register(PortfolioImage)
