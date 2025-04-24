from django.contrib import admin

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'avatar']


@admin.register(PlatformRules)
class PlatformRulesAdmin(admin.ModelAdmin):
    list_display = ("title", "updated_at")
    search_fields = ("title",)


admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(ArtworkForSale)
admin.site.register(PortfolioImage)
admin.site.register(Message)
admin.site.register(Report)
admin.site.register(ArtworkComment)
