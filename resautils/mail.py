# -*- coding: utf-8 -*-
from django.core.mail import send_mail, mail_admins
from django.template import Context, loader

from resarmll import settings

def send_email(to, subject, tmpl, ctx):
    t = loader.get_template(tmpl)
    subject = settings.DEFAULT_PREFIX_SUBJECT_EMAIL + subject
    send_mail(subject, t.render(Context(ctx)), None, to)

def send_admins(subject, tmpl, ctx):
    t = loader.get_template(tmpl)
    subject = settings.DEFAULT_PREFIX_SUBJECT_EMAIL + subject
    mail_admins(subject, t.render(Context(ctx)))