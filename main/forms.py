from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from .utils import transliterate
from .models import *


class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = {'username', 'email', 'first_name', 'last_name',}


class PostChangeForm(forms.Form):
    title = forms.CharField(max_length=150)
    body = forms.CharField()
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all())

    def clean_title(self):
        new_title = self.cleaned_data['title']
        if Post.objects.filter(title=new_title).exists():
            raise ValidationError('Титл <{}> уже существует!'.format(new_title))
        return new_title

    def save(self, post):


        post.title = self.cleaned_data['title']
        post.slug = transliterate(self.cleaned_data['title'].lower())
        post.body = self.cleaned_data['body']
        post.tags.set(self.cleaned_data['tags'])
        post.save()
        return post

class PostForm(forms.Form):
    title = forms.CharField(max_length=150)
    body = forms.CharField()
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all())

    def clean_title(self):
        new_title = self.cleaned_data['title']
        if Post.objects.filter(title=new_title).exists():
            raise ValidationError('Титл <{}> уже существует!'.format(new_title))
        return new_title


    def save(self, authorname):
        new_post = Post.objects.create(title=self.cleaned_data['title'],
            slug=transliterate(self.cleaned_data['title'].lower()),
            body = self.cleaned_data['body'],
            author = AdvUser.objects.get(username = authorname)
            )
        new_post.tags.set(self.cleaned_data['tags'])


        return new_post

class TagForm(forms.Form):
    title = forms.CharField(max_length=50)


    def clean_title(self):
        new_title = self.cleaned_data['title']

        if new_title == 'Create' or new_title == 'create':
            raise ValidationError('Tag may not be "Create"')
        return new_title


    def save(self):
        new_tag = Tag.objects.create(title=self.cleaned_data['title'],
            slug=transliterate(self.cleaned_data['title'].lower())
        )

        return new_tag


class UserCommentForm(forms.Form):
    body = forms.CharField()
    def save(self, author, post):
        new_comment = Comment.objects.create(author = author, post = post, content = self.cleaned_data['body'])



class GuestCommentForm(forms.Form):
    captcha = CaptchaField(label='Введите текст с картинки', error_messages={'invalid': 'Неправильный текст'})
    body = forms.CharField()
    def save(self, author, post):
        new_comment = Comment.objects.create(author = author, post = post, content = body)

class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput, help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput, help_text='Введите тот же самый пароль еще раз')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
