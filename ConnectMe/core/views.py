from django.shortcuts import HttpResponse,render, redirect, get_object_or_404
from ConnectMe.feeds.views import feeds
from django.contrib.auth.models import User
from ConnectMe.feeds.models import Feed
from ConnectMe.feeds.views import FEEDS_NUM_PAGES
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from ConnectMe.core.forms import ProfileForm, ChangePasswordForm
from django.contrib import messages
from django.conf import settings as django_settings
from PIL import Image
from ConnectMe.users.models import *
import os
import json 
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_protect,ensure_csrf_cookie


def home(request):
    if request.user.is_authenticated():
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except Exception, e:
            userprofile      = UserProfile()
            userprofile.user = request.user
            userprofile.save()
        return feeds(request)
    else:
        return render(request, 'users/login.html')

@login_required
def change(request):
    #import pdb; pdb.set_trace()
    user=request.user
    json_data = {
        'message' : 'Incorrect corrent password',
        'status' : 'error'
    }
    if request.method == 'POST':
        cur_pwd  = request.POST.get('cur_pwd')
        new_pwd  = request.POST.get('new_pwd')
        user1    = authenticate(username=user.username,password=cur_pwd)
        if user1 == user :
            user.set_password(new_pwd)
            user.save()
            json_data['message']  = 'Password changed successfully.'
            json_data['status'] = 'success'

    json_data = json.dumps(json_data)

    #import pdb; pdb.set_trace()
    return HttpResponse(json_data, content_type='application/json')

@login_required
def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    all_feeds = Feed.get_feeds().filter(user=page_user)
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    feeds     = paginator.page(1)
    from_feed = -1
    if feeds:
        from_feed = feeds[0].id
    return render(request, 'core/profile.html', {
        'page_user': page_user, 
        'feeds': feeds,
        'from_feed': from_feed,
        'page': 1
        })

@login_required
def settings(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            first_name                  = request.POST['first_name']
            last_name                   = request.POST['last_name']
            email                       = request.POST['email']
            phone_number                = request.POST['phone_number']
            address                     = request.POST['address']
            country                     = request.POST['country']
            date_of_birth               = request.POST['date_of_birth']
            gender                      = request.POST['gender']
            user_profile                = UserProfile.objects.get(user=user)
            user_profile.country        = country
            user_profile.address        = address
            user_profile.gender         = gender
            user_profile.phone_number   = phone_number
            user_profile.date_of_birth  = date_of_birth
            user_profile.save()
            user.first_name             = first_name[:30]
            user.last_name              = last_name[:30]
            user.email                  = email[:75]
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Your profile were successfully edited.')
    else:
        #user_profile = UserProfile.objects.get(user=user)
        form = ProfileForm(instance=user, initial={
            'email':user.email,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'gender':user.userprofile.gender,
            'phone_number':user.userprofile.phone_number,
            'date_of_birth':user.userprofile.date_of_birth,
            'address': user.userprofile.address,
            'country':user.userprofile.country
            })
    return render(request, 'core/settings.html', {'form':form})

@login_required
def picture(request):
    uploaded_picture = False
    try:
        if request.GET.get('upload_picture') == 'uploaded':
            uploaded_picture = True
    except Exception, e:
        pass
    return render(request, 'core/picture.html', {'uploaded_picture': uploaded_picture})

@login_required
def password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Your password were successfully changed.')
    else:
        form = ChangePasswordForm(instance=user)
    return render(request, 'core/password.html', {'form':form})

@login_required
def upload_picture(request):
    try:
        profile_pictures = django_settings.MEDIA_ROOT + '/profile_pictures/'
        if not os.path.exists(profile_pictures):
            os.makedirs(profile_pictures)
        f = request.FILES['picture']
        filename = profile_pictures + request.user.username + '.jpg'
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)    
        im = Image.open(filename)
        width, height = im.size
        if width > 350:
            new_width   = 350
            new_height  = (height * 350) / width
            new_size    = new_width, new_height
            im.thumbnail(new_size, Image.ANTIALIAS)
            im.save(filename)
        return redirect('/settings/picture/?upload_picture=uploaded')
    except Exception, e:
        return redirect('/settings/picture/')

@login_required
def save_uploaded_picture(request):
    try:
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        w = int(request.POST.get('w'))
        h = int(request.POST.get('h'))
        tmp_filename    = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '_tmp.jpg'
        filename        = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '.jpg'
        im              = Image.open(tmp_filename)
        cropped_im      = im.crop((x, y, w+x, h+y))
        cropped_im.thumbnail((200, 200), Image.ANTIALIAS)
        cropped_im.save(filename)
        os.remove(tmp_filename)
    except Exception, e:
        pass
    return redirect('/settings/picture/')