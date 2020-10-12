from django.shortcuts import render, get_object_or_404, redirect
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import signer
from .models import *
from .forms import ChangeUserInfoForm, RegisterUserForm, PostForm, TagForm, PostChangeForm, UserCommentForm, GuestCommentForm
from .utils import ObjectDetailMixin, transliterate

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


# @login_required
# def profile_post_add(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#
#             messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
#             return redirect('main:profile')
#     else:
#         form = PostForm(initial={'author': request.user.username})
#     context = {'form': form}
#     return render(request, 'main/profile_post_add.html', context)

class PostCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = PostForm(initial={'author': request.user.username, 'slug': 'sds'})
        return render(request, 'main/profile_post_add.html', context={'form': form})

    def post(self, request):
        bound_form = PostForm(request.POST)
        if bound_form.is_valid():
            new_post = bound_form.save()
            messages.add_message(request, messages.SUCCESS, 'Пост добавлен')
            return redirect('main:profile')
        return render(request, 'main/profile_post_add.html', context={'form': bound_form})



@login_required
def profile_post_change(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostChangeForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.add_message(request, messages.SUCCESS, 'Обьявление исправлено')
            return redirect('main:profile')
    else:
        form = PostChangeForm(instance=post)
    context = {'form': form}
    return render(request, 'main/profile_post_change.html', context)

@login_required
def profile_post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.add_message(request, messages.SUCCESS, 'Обьявление удалено')
        return redirect('main:profile')
    else:
        context = {'post':post}
        return render(request, 'main/profile_post_delete.html', context)


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
    object_list = Post.objects.filter(author = request.user.pk)
    paginator = Paginator(object_list, 5)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'main/profile.html', { 'page': page, 'posts': posts})


class MBLoginView(LoginView):
    template_name = 'main/login.html'

def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug__iexact = slug)
    return render(request, 'main/tag_detail.html', {'tag': tag})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug__iexact=slug)
    post_author = get_object_or_404(AdvUser, pk = post.author.pk);
    object_list = Comment.objects.filter(post=post)
    paginator = Paginator(object_list, 10)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)



    initial = {'post': post.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        initial['author'] = 'Гость'
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
            return redirect('/posts/{}'.format(slug))
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')


    context = {'page':page,'post': post, 'post_author': post_author, 'comments': comments, 'form': form}
    return render(request, 'main/post_detail.html', context)


def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'main/tag_list.html', {'tags': tags})


class TagCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = TagForm()
        return render(request, 'main/tag_create.html', context={'form': form})

    def post(self, request):
        bound_form = TagForm(request.POST)
        if bound_form.is_valid():
            new_tag = bound_form.save()
            messages.add_message(request, messages.SUCCESS, 'Тэг добавлен')
            return redirect('main:tag_list')
        return render(request, 'main/tag_create.html', context={'form': bound_form})


def post_list(request):
    object_list = Post.objects.all()
    paginator = Paginator(object_list, 5)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'main/index.html', {'page': page,'posts': posts})
# Create your views here.
