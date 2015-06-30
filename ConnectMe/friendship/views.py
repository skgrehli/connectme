from django.shortcuts import render_to_response,HttpResponse,render,redirect
from django.core.mail import send_mail
from ConnectMe.feeds.views import feeds
from django.conf import settings
from ConnectMe.users.forms import SignUpForm
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from .models import *
from django.template import RequestContext
#from djutils.decorators import async
from background_task import background
def friend_accept(request):
    code = request.GET.get('code')
    friendshiprequest = FriendshipRequest.objects.get(id=request.GET.get('code'))
    is_user=request.GET.get('is_user')
    if request.user.is_authenticated() and friendshiprequest.to_email==request.user.email:
        if friendshiprequest.get_status() == 'pending':
            friendshiprequest.accept()
            friendshiprequest.status = 'A'
            friendshiprequest.save()
        else:
            pass
        return feeds(request)
    if is_user == 'True':
        if friendshiprequest.get_status() == 'pending':
            friendshiprequest.accept()
            friendshiprequest.status = 'A'
            friendshiprequest.save()
        else:
            pass
        return redirect('/')
    else :
        return render(request, 'users/signup.html', {'form': SignUpForm(),'code':code})
    return HttpResponse("sandeep") 


def friend_list(request):
    friendshipmanager=FriendshipManager()
    friends=friendshipmanager.friends(request.user)
    for friend in friends:
        print friend.username
    return render_to_response('friendship/friendlist.html',
                          {'friends':friends},
                          context_instance=RequestContext(request))
    return HttpResponse("sandeep")




def invite_friends(request):
    user_request_list=None
    if request.method == 'POST':
        is_user           =  False
        email             =  request.POST.get('email')
        from_user         =  request.user
        user_request_list=FriendshipRequest.objects.all().filter(to_email=email).filter(from_user=from_user)
        print email
        if user_request_list :
            return HttpResponse("you friend request already exists")
        friendshiprequest =  FriendshipRequest()
        try:
            to_user  =  User.objects.get(email=email)
            is_user  =  True
            if from_user == to_user:
                return HttpResponse("you not send friend invitation itself")
        except Exception, e:
            pass
        else:
            friendshiprequest.to_user  = to_user
        friendshiprequest.from_user  = from_user
        friendshiprequest.to_email   = email
        friendshiprequest.save()
        print friendshiprequest.id
        send(email,friendshiprequest.id,request.user.username,is_user)#, schedule=90)
        print from_user
    return HttpResponse("Friend invitation successfully done ")
#@asyn
@background(schedule=60)
def send(email,code,sender_username,is_user):
    subject = u'Invitation to join ConnectMe App'
    link = 'http://%s/friend_accept?code=%s&is_user=%s' % (
      settings.SITE_HOST,
      code,
      is_user
    )
    template = get_template('friendship/invitation_email.html')

    context = Context({
      'name': email,
      'link': link,
      'sender': sender_username,
    })
    message = template.render(context)
    send_mail(
      subject, message,
      settings.DEFAULT_FROM_EMAIL, [email]
    )



# Create your views here.
