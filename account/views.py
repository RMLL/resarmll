# -*- coding: utf-8 -*-
import os.path

from django.db.models import Q
from django.utils.translation import check_for_language, ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django import forms
from django.conf import settings as django_settings

from resarmll import settings
from resarmll.account.forms import UserForm, UserFormModify, UserFormManagerCreate, UserFormManagerModify
from resarmll.account.models import UserProfile, NetworkAccess
from resarmll.resa.models import Badge
from resarmll.resa.utils import BadgeGenerator
from resarmll.utils.decorators import auto_render, manager_required

@login_required
def langcheck(request, redirect):
    lang_code = request.user.get_profile().language
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(django_settings.LANGUAGE_COOKIE_NAME, lang_code)
    return HttpResponseRedirect(redirect)

@auto_render
def register(request, tmpl):
    syserr = False
    if request.user.is_authenticated():
        return HttpResponseRedirect('/account/home/')

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                new_user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email']
                )
                new_user.set_password(form.cleaned_data['password'])
                new_user.first_name = form.cleaned_data['first_name']
                new_user.last_name = form.cleaned_data['last_name']
                new_user.save()
                badge = Badge.objects.filter(default=True)[0]
                new_profile = UserProfile(
                    user=new_user,
                    gender=form.cleaned_data['gender'],
                    address=form.cleaned_data['address'],
                    language=form.cleaned_data['language'],
                    country=form.cleaned_data['country'],
                    badge_type = badge,
                    badge_text=form.cleaned_data['badge_text'],
                    fingerprint=form.cleaned_data['fingerprint']
                )
                new_profile.save()
            except:
                syserr = True
            else:
                return HttpResponseRedirect('/account/register/complete/')
    else:
        form = UserForm()
    return tmpl, {'form': form, 'syserr': syserr}

@login_required
@auto_render
def home(request, tmpl):
    treasurer_name = settings.TREASURER_NAME
    treasurer_email = settings.TREASURER_EMAIL
    return tmpl, locals()

@login_required
@auto_render
def profile(request, tmpl):
    return tmpl, {}

@login_required
@auto_render
def profile_modify(request, tmpl):
    syserr = False
    cur_user = request.user
    if request.method == 'POST':
        form = UserFormModify(request.POST)
        if form.is_valid():
            try:
                cur_user.email = form.cleaned_data['email']
                cur_user.first_name = form.cleaned_data['first_name']
                cur_user.last_name = form.cleaned_data['last_name']
                if form.cleaned_data['password'] != '':
                    cur_user.set_password(form.cleaned_data['password'])
                cur_user.save()
                cur_profile = cur_user.get_profile()
                cur_profile.gender = form.cleaned_data['gender']
                cur_profile.address = form.cleaned_data['address']
                cur_profile.language = form.cleaned_data['language']
                cur_profile.country = form.cleaned_data['country']
                cur_profile.badge_text = form.cleaned_data['badge_text']
                cur_profile.fingerprint = form.cleaned_data['fingerprint']
                cur_profile.save()
            except:
                syserr = True
            else:
                return HttpResponseRedirect('/account/langchange/')
    else:
        form = UserFormModify()
        form.fill_from_user(cur_user)
    return tmpl, {'form': form, 'syserr': syserr}

@login_required
@auto_render
def profile_badge(request, tmpl):
    response_dct = {
        'badge_png': settings.MEDIA_URL + BadgeGenerator.get_path_png(request.user.id),
        'badge_big_png': settings.MEDIA_URL + BadgeGenerator.get_path_big_png(request.user.id),
        'badge_pdf': settings.MEDIA_URL + BadgeGenerator.get_path_pdf(request.user.id),
    }
    return tmpl, response_dct

@login_required
@auto_render
def wifi(request, tmpl):
    username = password = None
    try:
        access = NetworkAccess.objects.get(id=request.user.id)
        username = access.username
        password = access.password
    except:
        username = password = None
    return tmpl, locals()

@login_required
@manager_required
@auto_render
def create(request, tmpl):
    syserr = False
    create_success = False
    if request.method == 'POST':
        form = UserFormManagerCreate(request.POST)
        if form.is_valid():
            try:
                u = User(
                        username = form.cleaned_data['username'],
                        email = form.cleaned_data['email'],
                        first_name = form.cleaned_data['first_name'],
                        last_name = form.cleaned_data['last_name'])
                u.set_password(form.cleaned_data['password'])
                u.save()
                p = UserProfile(
                        user=u,
                        gender = form.cleaned_data['gender'],
                        address = form.cleaned_data['address'],
                        language = form.cleaned_data['language'],
                        country = form.cleaned_data['country'],
                        badge_text = form.cleaned_data['badge_text'],
                        fingerprint = form.cleaned_data['fingerprint'],
                        badge_type = form.cleaned_data['badge_type'],
                        notes =  form.cleaned_data['notes'],
                    payment_later=form.cleaned_data['payment_later'])
                p.save()
                create_success = True
            except:
                syserr = True
            else:
                create_success = True
                form = UserFormManagerCreate()
    else:
        form = UserFormManagerCreate()
    return tmpl, {'form': form, 'syserr': syserr, 'create_success': create_success}

@login_required
@manager_required
@auto_render
def search(request, tmpl):
    pattern = request.POST.get('pattern')
    if pattern is None:
        search_mode = False
        pattern = ''
    else:
        search_mode = True
    results = None
    if search_mode and pattern != '':
        results = User.objects.filter(Q(username__icontains = pattern) |
                Q(email__icontains = pattern) |
                Q(first_name__icontains = pattern) |
                Q(last_name__icontains = pattern)).order_by('id')
    return tmpl, locals()

@login_required
@manager_required
@auto_render
def edit(request, tmpl, user_id=None):
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            user = None
    syserr = False
    modify_success = False
    form = None
    if user:
        if request.method == 'POST':
            form = UserFormManagerModify(request.POST)
            if form.is_valid():
                #try:
                user.email = form.cleaned_data['email']
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                if form.cleaned_data['password'] != '':
                    user.set_password(form.cleaned_data['password'])
                user.save()
                p = user.get_profile()
                p.gender = form.cleaned_data['gender']
                p.address = form.cleaned_data['address']
                p.language = form.cleaned_data['language']
                p.country = form.cleaned_data['country']
                p.badge_text = form.cleaned_data['badge_text']
                p.fingerprint = form.cleaned_data['fingerprint']
                p.badge_type = form.cleaned_data['badge_type']
                p.notes =  form.cleaned_data['notes']
                p.payment_later = form.cleaned_data['payment_later']
                p.save()
                #except:
                    #syserr = True
                #else:
                #    modify_success = True
        else:
            form = UserFormManagerModify()
            form.fill_from_user(user)
    return tmpl, {'user_obj': user, 'form': form, 'syserr': syserr,
                    'modify_success': modify_success}

@login_required
@manager_required
@auto_render
def manage_badge(request, tmpl, user_id):
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            user = None

    response_dct = {
        'user_obj': user,
        'badge_png': settings.MEDIA_URL + BadgeGenerator.get_path_png(user_id),
        'badge_big_png': settings.MEDIA_URL + BadgeGenerator.get_path_big_png(user_id),
        'badge_pdf': settings.MEDIA_URL + BadgeGenerator.get_path_pdf(user_id),
        'badge_pdf_printer': settings.MEDIA_URL + BadgeGenerator.get_path_pdf_printer(user_id),
        'badge_pdf_printer_portait': settings.MEDIA_URL + BadgeGenerator.get_path_pdf_printer_portrait(user_id),
    }
    return tmpl, response_dct

@login_required
@manager_required
@auto_render
def manage_wifi(request, tmpl, user_id):
    user = username = password = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            user = None
        if user:
            try:
                access = NetworkAccess.objects.get(id=user.id)
                username = access.username
                password = access.password
            except:
                username = password = None

    return tmpl, {'user_obj': user, 'username': username, 'password': password}
