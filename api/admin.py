from django.contrib import admin
from .models import Account, Report, Task, News

# Register your models here.

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'authority_level', 'is_active']
    list_filter = ['authority_level', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'account', 'status', 'date_reported', 'address', 'latitude', 'longitude']
    list_filter = ['status', 'date_reported', 'has_task']
    search_fields = ['title', 'description', 'address']
    readonly_fields = ['date_reported']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'username', 'status']
    list_filter = ['status']
    search_fields = ['title', 'descirption', 'username__username']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'address']
    list_filter = ['date']
    search_fields = ['title', 'description', 'address']
