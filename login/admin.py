from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from login.models import BlockchainAccount


# Register your models here.
class BlockchainAccountInline(admin.StackedInline):
    model = BlockchainAccount
    can_delete = False
    verbose_name_plural = 'blockchainaccount'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (BlockchainAccountInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
