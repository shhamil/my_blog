from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View, ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from .forms import ChangeUserInfoForm, RegisterUserForm, PostForm, TagForm, PostChangeForm, UserCommentForm, \
    GuestCommentForm
from .models import *
from .utils import signer


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


class PostCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    template_name = 'main/profile_post_add.html'
    form_class = PostForm
    success_message = 'Пост добавлен'
    success_url = reverse_lazy('main:profile')

    def get_form_kwargs(self):
        kwargs = super(PostCreate, self).get_form_kwargs()
        kwargs['author'] = self.request.user
        return kwargs

class PostChange(LoginRequiredMixin, UpdateView):

    model = Post
    template_name = 'main/profile_post_change.html'
    form_class = PostChangeForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Пост изменен'



class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'main/profile_post_delete.html'
    success_url = reverse_lazy('main:profile')


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

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.request.user.id)


class MBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


class Profile(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 5
    template_name = 'main/profile.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Post.objects.filter(author=self.request.user.pk)
        return queryset


class MBLoginView(LoginView):
    template_name = 'main/login.html'


class TagDetail(DetailView):
    model = Tag


class PostDetail(DetailView):
    model = Post
    template_name = 'main/post_detail.html'

    def get_form_class(self):
        if self.request.user.is_authenticated:
            form_class = UserCommentForm
        else:
            form_class = GuestCommentForm
        return form_class

    def get_object(self):
        obj =  super().get_object()
        return obj

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.object)
        context['form'] = self.get_form_class()
        return context

    def post(self, request, slug):
        form = self.get_form_class()
        form = form(request.POST)
        if form.is_valid():
            form.save(self.request.user.username, self.get_object())
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен!')
            return redirect('/posts/{}'.format(slug))
        return render(request, self.template_name, {'form': form})


class TagList(ListView):
    queryset = Tag.objects.all()
    paginate_by = 2
    template_name = 'main/tag_list.html'
    context_object_name = 'tags'


class TagCreate(LoginRequiredMixin, CreateView):
    model = Tag
    template_name = 'main/tag_create.html'
    form_class = TagForm
    success_message = 'Тэг добавлен'
    success_url = reverse_lazy('main:tag_list')



class PostList(ListView):
    queryset = Post.objects.all()
    paginate_by = 5
    template_name = 'main/index.html'
    context_object_name = 'posts'
