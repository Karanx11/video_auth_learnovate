from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'is_verified', 'uploaded_at')
    readonly_fields = ('video', 'uploaded_at')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'full_name', 'user__email')
    actions = ['verify_selected', 'unverify_selected']

    def verify_selected(self, request, queryset):
        queryset.update(is_verified=True)
    verify_selected.short_description = "Mark selected profiles as verified"

    def unverify_selected(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_selected.short_description = "Mark selected profiles as unverified"

admin.site.register(Profile, ProfileAdmin)
