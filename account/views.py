# -*- coding: utf-8 -*-
import os.path

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.utils.translation import check_for_language
from django.utils.http import urlquote
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings as django_settings

from resarmll import settings
from account.forms import UserForm, UserFormModify, UserFormManagerCreate, UserFormManagerModify
from account.models import UserProfile, NetworkAccess
from resa.models import Badge
from resa.utils import BadgeGenerator
from resautils.decorators import auto_render, manager_required, reception_required

@login_required
def langcheck(request, redirect):
    lang_code = request.user.get_profile().language
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(django_settings.LANGUAGE_COOKIE_NAME, lang_code)
    return HttpResponseRedirect(redirect)

def register_set(request, redirect, code = None):
    if code:
        request.session['register_data'] = code
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
                badge = form.cleaned_data['badge_type']
                if not badge.userchoice:
                    badge = Badge.objects.filter(default=True)[0]
                if request.session.get('register_data'):
                    notes = "REGISTER_DATA:%s\n" % (request.session.get('register_data'))
                else:
                    notes = ""
                new_profile = UserProfile(
                    user=new_user,
                    gender=form.cleaned_data['gender'],
                    address=form.cleaned_data['address'],
                    zipcode=form.cleaned_data['zipcode'],
                    city=form.cleaned_data['city'],
                    country=form.cleaned_data['country'],
                    language=form.cleaned_data['language'],
                    badge_type = badge,
                    badge_text=form.cleaned_data['badge_text'],
                    comments=form.cleaned_data['comments'],
                    fingerprint=form.cleaned_data['fingerprint'],
                    notes = notes
                )
                new_profile.save()
            except Exception, e:
                print e
                syserr = True
            else:
                return HttpResponseRedirect('/account/register/complete/')
    else:
        form = UserForm()
    return tmpl, {'form': form, 'syserr': syserr}

@login_required
@auto_render
def home(request, tmpl):
    treasurer = settings.TREASURER_SETTINGS
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
                cur_profile.zipcode = form.cleaned_data['zipcode']
                cur_profile.city = form.cleaned_data['city']
                cur_profile.country = form.cleaned_data['country']
                cur_profile.language = form.cleaned_data['language']
                cur_profile.badge_text = form.cleaned_data['badge_text']
                cur_profile.comments = form.cleaned_data['comments']
                cur_profile.fingerprint = form.cleaned_data['fingerprint']
                badge = form.cleaned_data['badge_type']
                if badge:
                    if not badge.userchoice:
                        badge = Badge.objects.filter(default=True)[0]
                    cur_profile.badge_type = badge
                cur_profile.save()
            except Exception, e:
                print e
                syserr = True
            else:
                return HttpResponseRedirect('/account/langchange/')
    else:
        form = UserFormModify()
        user = User.objects.get(id=cur_user.id)
        form.fill_from_user(user)
    return tmpl, {'form': form, 'syserr': syserr}

@login_required
@auto_render
def profile_badge(request, tmpl):
    user =  request.user
    return tmpl, locals()

@login_required
def profile_badge_view(request, output = 'png', user_id = 0):
    response = HttpResponseForbidden()
    user_id = int(user_id)

    if user_id == request.user.id:
        filepath = content_type = content_disposition = None
        if output == 'png':
            filepath = BadgeGenerator.get_path_png(user_id)
            content_type = 'image/png'
            content_disposition = 'inline; filename=badge-%s_%d.png' % (urlquote(request.user.username), user_id)
        elif output == 'bigpng':
            filepath = BadgeGenerator.get_path_big_png(user_id)
            content_type = 'image/png'
            content_disposition = 'inline; filename=badgebig-%s_%d.png' % (urlquote(request.user.username), user_id)
        elif output == 'pdf':
            filepath = BadgeGenerator.get_path_pdf(user_id)
            content_type = 'application/pdf'
            content_disposition = 'attachement; filename=badge-%s_%d.pdf' % (urlquote(request.user.username), user_id)

        if filepath and os.path.exists(filepath):
            wrapper = FileWrapper(file(filepath))
            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Disposition'] = content_disposition
            response['Content-Length'] = os.path.getsize(filepath)

    return response

@login_required
@auto_render
def netparams(request, tmpl):
    username = password = None
    try:
        access = NetworkAccess.objects.get(id=request.user.id)
        username = access.username
        password = access.password
    except:
        username = password = None
    sxb_ip = "89.234.%d.%d" % (168 + request.user.id/256, request.user.id % 256)
    return tmpl, locals()

@login_required
@reception_required
@auto_render
def create(request, tmpl):
    syserr = False
    create_success = False
    user_obj = None
    if request.method == 'POST':
        form = UserFormManagerCreate(request.POST)
        if form.is_valid():
            try:
                user_obj = User(
                        username = form.cleaned_data['username'],
                        email = form.cleaned_data['email'],
                        first_name = form.cleaned_data['first_name'],
                        last_name = form.cleaned_data['last_name'])
                user_obj.set_password(form.cleaned_data['password'])
                user_obj.save()
                p = UserProfile(
                        user=user_obj,
                        gender = form.cleaned_data['gender'],
                        address = form.cleaned_data['address'],
                        country = form.cleaned_data['country'],
                        zipcode = form.cleaned_data['zipcode'],
                        city = form.cleaned_data['city'],
                        language = form.cleaned_data['language'],
                        badge_text = form.cleaned_data['badge_text'],
                        comments =  form.cleaned_data['comments'],
                        fingerprint = form.cleaned_data['fingerprint'],
                        badge_type = form.cleaned_data['badge_type'],
                        notes =  form.cleaned_data['notes'],
                    payment_later=form.cleaned_data['payment_later'])
                p.save()
                create_success = True
            except Exception, e:
                print e
                syserr = True
            else:
                create_success = True
                form = UserFormManagerCreate()
    else:
        form = UserFormManagerCreate()
    return tmpl, {'user_obj': user_obj, 'form': form, 'syserr': syserr, 'create_success': create_success}

@login_required
@reception_required
@auto_render
def search(request, tmpl):
    pattern = request.POST.get('pattern')

    # search by id
    searchuser= None
    try:
        searchuser = User.objects.get(id=int(pattern))
    except:
        pass
    if searchuser:
        if request.user.get_profile().is_reception:
            return HttpResponseRedirect('/account/edit/'+str(searchuser.id))
        else:
            return HttpResponseRedirect('/resa/manage_orders/%d' % (searchuser.id))

    results = None
    try:
        badge = Badge.objects.get(id=int(request.POST.get('badge')))
    except:
        badge = None

    if pattern is None:
        search_mode = False
        pattern = ''
    else:
        search_mode = True

    if search_mode and pattern != '':
        if badge:
            results = User.objects.filter(
                Q(username__icontains = pattern) |
                Q(email__icontains = pattern) |
                Q(first_name__icontains = pattern) |
                Q(last_name__icontains = pattern),userprofile__badge_type=badge).order_by('id')
        else:
            results = User.objects.filter(Q(username__icontains = pattern) |
                Q(email__icontains = pattern) |
                Q(first_name__icontains = pattern) |
                Q(last_name__icontains = pattern)).order_by('id')
    elif badge and pattern == '':
        results = User.objects.filter(userprofile__badge_type=badge).order_by('id')

    if results and len(results) == 1:
        if request.user.get_profile().is_reception:
            return HttpResponseRedirect('/account/edit/'+str(results[0].id))
        else:
            return HttpResponseRedirect('/resa/manage_orders/%d' % (results[0].id))

    badges = Badge.objects.all()
    return tmpl, locals()

@login_required
@manager_required
@auto_render
def comments(request, tmpl):
    results = User.objects.exclude(Q(userprofile__comments__exact = '')).order_by('-id')
    return tmpl, locals()

@login_required
@reception_required
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
                try:
                    user.email = form.cleaned_data['email']
                    user.first_name = form.cleaned_data['first_name']
                    user.last_name = form.cleaned_data['last_name']
                    if form.cleaned_data['password'] != '':
                        user.set_password(form.cleaned_data['password'])
                    user.save()
                    p = user.get_profile()
                    p.gender = form.cleaned_data['gender']
                    p.address = form.cleaned_data['address']
                    p.zipcode = form.cleaned_data['zipcode']
                    p.city = form.cleaned_data['city']
                    p.country = form.cleaned_data['country']
                    p.language = form.cleaned_data['language']
                    p.badge_text = form.cleaned_data['badge_text']
                    p.comments =  form.cleaned_data['comments']
                    p.fingerprint = form.cleaned_data['fingerprint']
                    p.badge_type = form.cleaned_data['badge_type']
                    p.notes =  form.cleaned_data['notes']
                    p.payment_later = form.cleaned_data['payment_later']
                    p.order_staff = form.cleaned_data['order_staff']
                    p.save()
                except Exception, e:
                    print e
                    syserr = True
                else:
                    modify_success = True
        else:
            form = UserFormManagerModify()
            form.fill_from_user(user)
    return tmpl, {'user_obj': user, 'form': form, 'syserr': syserr,
                    'modify_success': modify_success}

@login_required
@reception_required
@auto_render
def manage_badge(request, tmpl, user_id):
    user_obj = None
    if user_id:
        try:
            user_obj = User.objects.get(id=user_id)
        except:
            user_obj = None

    return tmpl, locals()

@login_required
@reception_required
def manage_badge_view(request, output = 'png', user_id = 0):
    response = HttpResponseForbidden()

    user = None
    try:
        user = User.objects.get(id=int(user_id))
    except:
        user = None

    if user:
        filepath = content_type = content_disposition = None
        if output == 'png':
            filepath = BadgeGenerator.get_path_png(user_id)
            content_type = 'image/png'
            content_disposition = 'inline; filename=badge-%s_%d.png' % (urlquote(user.username), user.id)
        elif output == 'bigpng':
            filepath = BadgeGenerator.get_path_big_png(user_id)
            content_type = 'image/png'
            content_disposition = 'inline; filename=badgebig-%s_%d.png' % (urlquote(user.username), user.id)
        elif output == 'pdf':
            filepath = BadgeGenerator.get_path_pdf(user_id)
            content_type = 'application/pdf'
            content_disposition = 'attachement; filename=badge-%s_%d.pdf' % (urlquote(user.username), user.id)

        if filepath and os.path.exists(filepath):
            wrapper = FileWrapper(file(filepath))
            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Disposition'] = content_disposition
            response['Content-Length'] = os.path.getsize(filepath)

    return response

@login_required
@reception_required
@auto_render
def manage_netparams(request, tmpl, user_id):
    user = username = password = sxb_ip = None
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
            sxb_ip = "89.234.%d.%d" % (168 + user.id/256, user.id % 256)
    return tmpl, {'user_obj': user, 'username': username, 'password': password, 'sxb_ip': sxb_ip}
