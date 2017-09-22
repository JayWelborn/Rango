from django.contrib import admin

from .models import Category, Page, UserProfile


class PageInline(admin.TabularInline):
    
    model = Page
    extra = 1
    ordering = ['pk']


class CategoryAdmin(admin.ModelAdmin):
    
    inlines = [PageInline]
    list_display = ('name', 'views', 'likes')
    prepopulated_fields = {'slug': ('name',)}


class PageAdmin(admin.ModelAdmin):

    list_display = ('title', 'category', 'url')


# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)