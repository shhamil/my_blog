from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from django.views.generic import View
from django.contrib.auth import logout
from django.contrib import messages

from .utils import signer
from .models import *
from .forms import ChangeUserInfoForm, RegisterUserForm
from .utils import ObjectDetailMixin

def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'

class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk = self.user_id)


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class MBPaswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Личные данные пользователям изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class MBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


@login_required
def profile(request):
    posts = Post.objects.filter(author = request.user.pk)

    return render(request, 'main/profile.html', {'posts': posts})


class MBLoginView(LoginView):
    template_name = 'main/login.html'

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug__iexact = slug)
    return render(request, 'main/tag_detail.html', {'tag': tag})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug__iexact=slug)
    post_author = get_object_or_404(AdvUser, pk = post.author.pk);
    return render(request, 'main/post_detail.html', {'post': post, 'post_author': post_author})


def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'main/tag_list.html', {'tags': tags})


def post_list(request):
    posts = Post.objects.all()
    return render(request, 'main/index.html', {'posts': posts})
# Create your views here.
