from django.contrib import admin

from .models import AdvUser, Post, Tag

admin.site.register(AdvUser)
admin.site.register(Post)
admin.site.register(Tag)
# Register your models here.
