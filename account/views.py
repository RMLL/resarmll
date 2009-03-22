# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from account.forms import UserForm, UserFormModify
from account.models import UserProfile

def register(request,
            template_name='account/register.html',
            extra_context=None):
    syserr = False
    if request.user.is_authenticated():
        return HttpResponseRedirect('/account/profile/')

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
                new_profile = UserProfile(
                    user=new_user,
                    address=form.cleaned_data['address'],
                    language=form.cleaned_data['language'],
                    country=form.cleaned_data['country'],
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

    return render_to_response(template_name, {'form': form, 'syserr': syserr})

def resendpwd(request,
            template_name='account/resendpwd.html',
            extra_context=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/account/profile/')

    return render_to_response(template_name)

@login_required
def profile(request,
            template_name='account/profile.html',
            extra_context=None):
    return render_to_response(template_name, {'user': request.user})

def profile_modify(request,
            template_name='account/profile/modify.html',
            extra_context=None):
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
                cur_profile.address = form.cleaned_data['address']
                cur_profile.language = form.cleaned_data['language']
                cur_profile.country = form.cleaned_data['country']
                cur_profile.badge_text = form.cleaned_data['badge_text']
                cur_profile.fingerprint = form.cleaned_data['fingerprint']
                cur_profile.save()
            except:
                syserr = True
            else:
                return HttpResponseRedirect('/account/profile/')
    else:
        form = UserFormModify()
        form.fill_from_user(cur_user)

    return render_to_response(template_name, {'form': form, 'syserr': syserr})
