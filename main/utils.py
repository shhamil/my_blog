from django.template.loader import render_to_string
from django.core.signing import Signer
from django.conf import settings
from blog.settings import ALLOWED_HOSTS
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .models import *


signer = Signer()

def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host='http://localhost:8000'
    context = {'user': user, 'host': host, 'sign':signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    subject = subject.replace('\n', '')
    user.email_user(subject, body_text)

class ObjectDetailMixin:
    model = None
    template = None

    def get(self, request, slug):
        # post = Post.objects.get(slug__iexact=slug)
        obj = get_object_or_404(self.model, slug__iexact=slug)
        return render(request, self.template, context={self.model.__name__.lower(): obj})
