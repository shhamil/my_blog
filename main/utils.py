# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.core.signing import Signer
from django.conf import settings
from blog.settings import ALLOWED_HOSTS
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .models import *
import re

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


def transliterate(string):
     capital_letters = {u'А': u'A',
                        u'Б': u'B',
                        u'В': u'V',
                        u'Г': u'G',
                        u'Д': u'D',
                        u'Е': u'E',
                        u'Ё': u'E',
                        u'З': u'Z',
                        u'И': u'I',
                        u'Й': u'Y',
                        u'К': u'K',
                        u'Л': u'L',
                        u'М': u'M',
                        u'Н': u'N',
                        u'О': u'O',
                        u'П': u'P',
                        u'Р': u'R',
                        u'С': u'S',
                        u'Т': u'T',
                        u'У': u'U',
                        u'Ф': u'F',
                        u'Х': u'H',
                        u'Ъ': u'',
                        u'Ы': u'Y',
                        u'Ь': u'',
                        u'Э': u'E',}
     capital_letters_transliterated_to_multiple_letters = {u'Ж': u'Zh',
                                                           u'Ц': u'Ts',
                                                           u'Ч': u'Ch',
                                                           u'Ш': u'Sh',
                                                           u'Щ': u'Sch',
                                                           u'Ю': u'Yu',
                                                           u'Я': u'Ya',}

     lower_case_letters = {u'а': u'a',
                        u'б': u'b',
                        u'в': u'v',
                        u'г': u'g',
                        u'д': u'd',
                        u'е': u'e',
                        u'ё': u'e',
                        u'ж': u'zh',
                        u'з': u'z',
                        u'и': u'i',
                        u'й': u'y',
                        u'к': u'k',
                        u'л': u'l',
                        u'м': u'm',
                        u'н': u'n',
                        u'о': u'o',
                        u'п': u'p',
                        u'р': u'r',
                        u'с': u's',
                        u'т': u't',
                        u'у': u'u',
                        u'ф': u'f',
                        u'х': u'h',
                        u'ц': u'ts',
                        u'ч': u'ch',
                        u'ш': u'sh',
                        u'щ': u'sch',
                        u'ъ': u'',
                        u'ы': u'y',
                        u'ь': u'',
                        u'э': u'e',
                        u'ю': u'yu',
                        u'я': u'ya',}

     for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.items():
         string = re.sub(r"%s([а-я])" % cyrillic_string, r'%s\1' % latin_string, string)

     for dictionary in (capital_letters, lower_case_letters):
         for cyrillic_string, latin_string in dictionary.items():
             string = string.replace(cyrillic_string, latin_string)

     for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.items():
         string = string.replace(cyrillic_string, latin_string.upper())

     return string.replace(' ', '_')
