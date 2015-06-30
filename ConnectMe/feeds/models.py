from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.html import escape
from django.db.models import Q
import bleach
from ConnectMe.friendship.models import *


class Feed(models.Model):
    user        = models.ForeignKey(User)
    created_at  = models.DateTimeField(auto_now_add=True)
    post        = models.TextField(max_length=255)
    parent      = models.ForeignKey('Feed', null=True, blank=True)
    likes       = models.IntegerField(default=0)
    comments    = models.IntegerField(default=0)
    Visibility  = (('P','public'),('O','Only_me'),('F','Friends'),)
    visibility  = models.CharField(max_length=1,choices=Visibility,default='P')
    updated_at  = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = _('Feed')
        verbose_name_plural = _('Feeds')
        ordering = ('-created_at',)

    def __unicode__(self):
        return self.post
    def get_visibility(self):
        if self.visibility=='P':
            visi_msg='public'
        if self.visibility=='O':
            visi_msg='Only_me'
        if self.visibility=='F':
            visi_msg='Friends'
        return visi_msg

    @staticmethod
    def get_feeds(from_feed=None):
        if from_feed is not None:
            feeds = Feed.objects.filter(parent=None, id__lte=from_feed)
        else:
            feeds = Feed.objects.filter(parent=None)
        return feeds

    @staticmethod
    def get_feeds_after(feed,request_user):
        feeds_new=[]
        friendship_manager=FriendshipManager()
        feeds = Feed.objects.filter(parent=None, id__gt=feed)
        for feed in feeds:
            if feed.visibility=='P' or feed.user==request_user:
                feeds_new.append(feed)
            elif feed.visibility=='F':
                if friendship_manager.are_friends(request_user,feed.user):
                    feeds_new.append(feed)

        return feeds_new

    def get_comments(self):
        return Feed.objects.filter(parent=self).order_by('created_at')

    def calculate_comments(self):
        self.comments = Feed.objects.filter(parent=self).count()
        self.save()
        return self.comments

    def comment(self, user, post):
        feed_comment = Feed(user=user, post=post, parent=self)
        feed_comment.save()
        self.comments = Feed.objects.filter(parent=self).count()
        self.save()
        return feed_comment

    def linkfy_post(self):
        return bleach.linkify(escape(self.post))
