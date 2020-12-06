from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from django.shortcuts import reverse
from .utils import *

user_registrated = Signal(providing_args=['instance'])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registrated.connect(user_registrated_dispatcher)


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')

    def delete(self, *args, **kwargs):
        for post in self.post_set.all():
            post.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Post(models.Model):
    title = models.CharField(max_length=150, db_index=True, verbose_name='Заголовок поста')
    slug = models.SlugField(max_length=150, unique=True)
    body = models.TextField(blank=True, db_index=True, verbose_name='Текст поста')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор поста')
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        self.slug = transliterate(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return '{}'.format(self.title)


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return '{}'.format(self.title)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.CharField(max_length=50, verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['-created_at']
