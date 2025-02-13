from django.contrib import admin

from user.models import EmailVerification, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)
    search_fields = ('username',)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'valid')
    fields = ('code', 'user', 'created', 'valid')
    readonly_fields = ('created',)
