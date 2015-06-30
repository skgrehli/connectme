from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from ConnectMe.feeds.models import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.core.context_processors import csrf
import json
from ConnectMe.friendship.models import *
from django.contrib.auth.decorators import login_required
from ConnectMe.decorators import ajax_required

FEEDS_NUM_PAGES = 20

@login_required
def feeds(request):
    all_feeds_new=[]
    all_feeds = Feed.get_feeds()
    friendship_manager=FriendshipManager()
    for feed in all_feeds :
        if feed.visibility=='P' or feed.user==request.user:
            all_feeds_new.append(feed)
        elif feed.visibility=='F':
            if friendship_manager.are_friends(request.user,feed.user):
                all_feeds_new.append(feed)
    paginator = Paginator(all_feeds_new, FEEDS_NUM_PAGES)
    feeds = paginator.page(1)
    from_feed = -1
    if feeds:
        from_feed = feeds[0].id
    return render(request, 'feeds/feeds.html', {
        'feeds': feeds, 
        'from_feed': from_feed, 
        'user':request.user,
        'page': 1,
        })

def feed(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    print 'sandeep'
    return render(request, 'feeds/feed.html', {'feed': feed})

@login_required
@ajax_required
def load(request):
    all_feeds_new=[]
    friendship_manager=FriendshipManager()
    from_feed = request.GET.get('from_feed')
    page = request.GET.get('page')
    feed_source = request.GET.get('feed_source')
    all_feeds = Feed.get_feeds(from_feed)
    for feed in all_feeds :
        if feed.visibility=='P' or feed.user==request.user:
            all_feeds_new.append(feed)
            print feed
        elif feed.visibility=='F':
            if friendship_manager.are_friends(request.user,feed.user):
                all_feeds_new.append(feed)
                print feed
    if feed_source != 'all':
        all_feeds = all_feeds_new.filter(user__id=feed_source)
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    try:
        feeds = paginator.page(page)
    except PageNotAnInteger:
        return HttpResponseBadRequest()
    except EmptyPage:
        feeds = []
    html = u''
    csrf_token = unicode(csrf(request)['csrf_token'])
    for feed in feeds:
        html = u'{0}{1}'.format(html, render_to_string('feeds/partial_feed.html', {
            'feed': feed,
            'csrf_token': csrf_token
            })
        )
    return HttpResponse(html)

def _html_feeds(last_feed, user, csrf_token, feed_source='all'):
    feeds = Feed.get_feeds_after(last_feed,user)
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    html = u''
    for feed in feeds:
        html = u'{0}{1}'.format(html, render_to_string('feeds/partial_feed.html', {
            'feed': feed,
            'user': user,
            'csrf_token': csrf_token
            })
        )
    return html

@login_required
@ajax_required
def load_new(request):
    last_feed = request.GET.get('last_feed')
    user = request.user
    csrf_token = unicode(csrf(request)['csrf_token'])
    html = _html_feeds(last_feed, user, csrf_token)
    return HttpResponse(html)

@login_required
@ajax_required
def check(request):
    last_feed = request.GET.get('last_feed')
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds_after(last_feed,request.user)
    print feeds
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    if feeds == []:
        count=0
    else:
        print feeds
        print len(feeds)
        count = len(feeds)
    return HttpResponse(count)

@login_required
@ajax_required
def post(request):
    last_feed = request.POST.get('last_feed')
    user = request.user
    csrf_token = unicode(csrf(request)['csrf_token'])
    feed = Feed()
    feed.user = user
    post = request.POST['post']
    visibility=request.POST['visibility']
    post = post.strip()
    if len(post) > 0:
        feed.post = post[:255]
        feed.visibility=visibility
        feed.save()
    html = _html_feeds(last_feed, user, csrf_token)
    return HttpResponse(html)
@login_required
@ajax_required
def comment(request):
    if request.method == 'POST':
        feed_id = request.POST['feed']
        feed = Feed.objects.get(pk=feed_id)
        post = request.POST['post']
        post = post.strip()
        if len(post) > 0:
            post = post[:255]
            user = request.user
            feed.comment(user=user, post=post)
            #user.profile.notify_commented(feed)
            #user.profile.notify_also_commented(feed)
        return render(request, 'feeds/partial_feed_comments.html', {'feed': feed})
    else:
        feed_id = request.GET.get('feed')
        print feed_id
        feed = Feed.objects.get(pk=feed_id)
        print feed.get_comments()
        for comment in feed.get_comments() :
            print comment.user
        return render(request, 'feeds/partial_feed_comments.html', {'feed': feed})

@login_required
@ajax_required
def update(request):
    feeds_new=[]
    first_feed = request.GET.get('first_feed')
    last_feed = request.GET.get('last_feed')
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds().filter(id__range=(last_feed, first_feed))
    for feed in feeds :
        if feed.visibility=='P' or feed.user==request.user:
            feeds_new.append(feed)
    if feed_source != 'all':
        feeds = feeds_new.filter(user__id=feed_source)
    dump = {}
    for feed in feeds:
        dump[feed.pk] = {'likes': feed.likes, 'comments': feed.comments}
    data = json.dumps(dump)
    return HttpResponse(data, content_type='application/json')

@login_required
@ajax_required
def track_comments(request):
    feed_id = request.GET.get('feed')
    feed = Feed.objects.get(pk=feed_id)
    return render(request, 'feeds/partial_feed_comments.html', {'feed': feed})

@login_required
@ajax_required
def remove(request):
    try:
        feed_id = request.POST.get('feed')
        feed = Feed.objects.get(pk=feed_id)
        print feed_id
        if feed.user == request.user:
            parent = feed.parent
            feed.delete()
            if parent:
                parent.calculate_comments()
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception, e:
        return HttpResponseBadRequest()