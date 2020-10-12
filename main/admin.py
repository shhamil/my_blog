from django.contrib import admin

from .models import AdvUser, Post, Tag, Comment

admin.site.register(AdvUser)
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)
# Register your models here.
