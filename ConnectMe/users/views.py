from django.shortcuts import HttpResponse,render, redirect
from django.contrib.auth import authenticate, login
from ConnectMe.users.forms import SignUpForm
from ConnectMe.friendship.models import *
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset, password_reset_confirm
import json 
from django.core.urlresolvers import reverse
"""
users views
"""
from django.contrib.auth import views

def reset(request):
    return password_reset(request, template_name='users/reset.html',
        email_template_name='users/reset_email.html',
        subject_template_name='users/reset_subject.txt',
        post_reset_redirect=reverse('success'))

def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='users/reset_confirm.html',
        uidb64=uidb64, token=token, post_reset_redirect=reverse('login'))

def success(request):
  return render(request, "users/success.html")



def login(request, *args, **kwargs):
    print 'sandeep'
    if request.method == 'POST':
        print request.POST.get('remember_me')
        if request.POST.get('remember_me', None):
            request.session.set_expiry(604800)
        else:
            request.session.set_expiry(0)
    return views.login(request, *args, **kwargs)


@login_required
def find_friend(request):
    #user=request.user
    json_data=[]
    users=User.objects.all()
    for user_crrent in users:
        json_data.append(user_crrent.email)
    json_data = json.dumps(json_data)

    #import pdb; pdb.set_trace()
    return HttpResponse(json_data, content_type='application/json')



 
def login_maybe_remember(request, *args, **kwargs):
    """
    Login, with the addition of 'remember-me' functionality. If the
    remember-me checkbox is checked, the session is remembered for
    SESSION_COOKIE_AGE seconds. If unchecked, the session expires at
    browser close.
 
    - https://docs.djangoproject.com/en/1.7/ref/settings/#std:setting-SESSION_COOKIE_AGE
    - https://docs.djangoproject.com/en/1.7/topics/http/sessions/#django.contrib.sessions.backends.base.SessionBase.set_expiry
    - https://docs.djangoproject.com/en/1.7/topics/http/sessions/#django.contrib.sessions.backends.base.SessionBase.get_expire_at_browser_close
    """
    if request.method == 'POST' and not request.POST.get('remember', None):
        #This is a login attempt and the checkbox is not checked.
        request.session.set_expiry(0)
 
    # print(request.session.get_expiry_age())
    # print(request.session.get_expire_at_browser_close())
 
    return login(request, *args, **kwargs)

def signup(request):
    if request.method == 'POST':
        import pdb
        #pdb.set_trace()
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'users/signup.html', {'form': form})
        else:
            username         = form.cleaned_data.get('username')
            email            = form.cleaned_data.get('email')
            password         = form.cleaned_data.get('password')
            User.objects.create_user(username=username, password=password, email=email)
            user             = authenticate(username=username, password=password)
            if request.POST.get('code'):
                friendshiprequest = FriendshipRequest.objects.get(id=request.POST.get('code'))
                if friendshiprequest.to_email==email:
                    if friendshiprequest.get_status() == 'pending':
                        friendshiprequest.to_user=user
                        friendshiprequest.save()
                        friendshiprequest.accept()
                        friendshiprequest.status = 'A'
                        friendshiprequest.save()
                        print 'sandeep'
            userprofile      = UserProfile()
            userprofile.user = user
            userprofile.save()
            login(request, user)
            #from_addr = "sgoswami@isystango.com"
            #recipient_list = ["rmishra@isystango.com"]
            #send_mail("New comment added",'hiiiii', from_addr, recipient_list) 
            #email = EmailMessage('Hello', 'World', to=['rmishra@osystango.com'])
            #email.send()
            return redirect('/')
    else:
        return render(request, 'users/signup.html', {'form': SignUpForm()})
