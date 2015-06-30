from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import datetime
from django.core.cache import cache
CACHE_TYPES = {
    'friends': 'f-%d',
    'followers': 'fo-%d',
    'following': 'fl-%d',
    'requests': 'fr-%d',
    'sent_requests': 'sfr-%d',
    'unread_requests': 'fru-%d',
    'unread_request_count': 'fruc-%d',
    'read_requests': 'frr-%d',
    'rejected_requests': 'frj-%d',
    'unrejected_requests': 'frur-%d',
    'unrejected_request_count': 'frurc-%d',
}

BUST_CACHES = {
    'friends': ['friends'],
    'followers': ['followers'],
    'following': ['following'],
    'requests': [
        'requests',
        'unread_requests',
        'unread_request_count',
        'read_requests',
        'rejected_requests',
        'unrejected_requests',
        'unrejected_request_count',
    ],
    'sent_requests': ['sent_requests'],
}


def cache_key(type, user_pk):
    """
    Build the cache key for a particular type of cached value
    """
    return CACHE_TYPES[type] % user_pk


def bust_cache(type, user_pk):
    """
    Bust our cache for a given type, can bust multiple caches
    """
    bust_keys = BUST_CACHES[type]
    keys = [CACHE_TYPES[k] % user_pk for k in bust_keys]
    cache.delete_many(keys)


















class FriendshipRequest(models.Model):
    """ Model to represent friendship requests """
    request_status=(('A','accepted'),('R','rejected'),('P','pending'),)
    from_user = models.ForeignKey(User, related_name='friendship_requests_sent')
    to_user = models.ForeignKey(User, related_name='friendship_requests_received',null=True)
    message = models.TextField(_('Message'), blank=True)
    to_email=models.EmailField( blank=True)
    status=models.CharField(max_length=1,choices=request_status,default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_request():
        pass

    def get_status(self):
        if self.status=='P':
            status_msg='pending'
        if self.status=='A':
            status_msg='accepted'
        if self.status=='R':
            status_msg='rejected'
        return status_msg
    @classmethod
    def remove_friend_cronjob(cls):
        friendship_requests=FriendshipRequest.objects.filter(status='P')
        for friendship_request in friendship_requests:
            duff_day=datetime.date.today()-friendship_request.updated_at.date()
            if duff_day.days >= 1 :
                friendship_request.status='R'
                friendship_request.save()
        return True


    def accept(self):
        """ Accept this friendship request """
        relation1 = Friend.objects.create(
            from_user=self.from_user,
            to_user=self.to_user
        )

        relation2 = Friend.objects.create(
            from_user=self.to_user,
            to_user=self.from_user
        )

        # friendship_request_accepted.send(
        #     sender=self,
        #     from_user=self.from_user,
        #     to_user=self.to_user
        # )

        # self.delete()

        # Delete any reverse requests
        # FriendshipRequest.objects.filter(
        #     from_user=self.to_user,
        #     to_user=self.from_user
        # ).delete()

        # Bust requests cache - request is deleted
        # bust_cache('requests', self.to_user.pk)
        # bust_cache('sent_requests', self.from_user.pk)
        # # Bust reverse requests cache - reverse request might be deleted
        # bust_cache('requests', self.from_user.pk)
        # bust_cache('sent_requests', self.to_user.pk)
        # # Bust friends cache - new friends added
        # bust_cache('friends', self.to_user.pk)
        # bust_cache('friends', self.from_user.pk)

        return True

    def reject(self):
        """ reject this friendship request """
        self.rejected = timezone.now()
        self.save()
        friendship_request_rejected.send(sender=self)
        bust_cache('requests', self.to_user.pk)

    def cancel(self):
        """ cancel this friendship request """
        self.delete()
        friendship_request_canceled.send(sender=self)
        bust_cache('requests', self.to_user.pk)
        bust_cache('sent_requests', self.from_user.pk)
        return True




class FriendshipManager(models.Manager):
    """ Friendship manager """

    def friends(self, user):
        """ Return a list of all friends """
        key = cache_key('friends', user.pk)
        friends = cache.get(key)

        if friends is None:
            qs = Friend.objects.select_related('from_user', 'to_user').filter(to_user=user).all()
            friends = [u.from_user for u in qs]
            cache.set(key, friends)

        return friends

    def requests(self, user):
        """ Return a list of friendship requests """
        key = cache_key('requests', user.pk)
        requests = cache.get(key)

        if requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user).all()
            requests = list(qs)
            cache.set(key, requests)

        return requests

    def sent_requests(self, user):
        """ Return a list of friendship requests from user """
        key = cache_key('sent_requests', user.pk)
        requests = cache.get(key)

        if requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                from_user=user).all()
            requests = list(qs)
            cache.set(key, requests)

        return requests

    def unread_requests(self, user):
        """ Return a list of unread friendship requests """
        key = cache_key('unread_requests', user.pk)
        unread_requests = cache.get(key)

        if unread_requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                viewed__isnull=True).all()
            unread_requests = list(qs)
            cache.set(key, unread_requests)

        return unread_requests

    def unread_request_count(self, user):
        """ Return a count of unread friendship requests """
        key = cache_key('unread_request_count', user.pk)
        count = cache.get(key)

        if count is None:
            count = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                viewed__isnull=True).count()
            cache.set(key, count)

        return count

    def read_requests(self, user):
        """ Return a list of read friendship requests """
        key = cache_key('read_requests', user.pk)
        read_requests = cache.get(key)

        if read_requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                viewed__isnull=False).all()
            read_requests = list(qs)
            cache.set(key, read_requests)

        return read_requests

    def add_friend(self, from_user, to_user, message=None):
        """ Create a friendship request """
        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if message is None:
            message = ''

        request, created = FriendshipRequest.objects.get_or_create(
            from_user=from_user,
            to_user=to_user,
            message=message,
        )

        if created is False:
            raise AlreadyExistsError("Friendship already requested")

        bust_cache('requests', to_user.pk)
        bust_cache('sent_requests', from_user.pk)
        friendship_request_created.send(sender=request)

        return request

    def remove_friend(self, to_user, from_user):
        """ Destroy a friendship relationship """
        try:
            qs = Friend.objects.filter(
                Q(to_user=to_user, from_user=from_user) |
                Q(to_user=from_user, from_user=to_user)
            ).distinct().all()

            if qs:
                friendship_removed.send(
                    sender=qs[0],
                    from_user=from_user,
                    to_user=to_user
                )
                qs.delete()
                bust_cache('friends', to_user.pk)
                bust_cache('friends', from_user.pk)
                return True
            else:
                return False
        except Friend.DoesNotExist:
            return False

    def are_friends(self, user1, user2):
        """ Are these two users friends? """
        friends1 = cache.get(cache_key('friends', user1.pk))
        friends2 = cache.get(cache_key('friends', user2.pk))
        if friends1 and user2 in friends1:
            return True
        elif friends2 and user1 in friends2:
            return True
        else:
            try:
                Friend.objects.get(to_user=user1, from_user=user2)
                return True
            except Friend.DoesNotExist:
                return False





class Friend(models.Model):
    """ Model to represent Friendships """
    to_user = models.ForeignKey(User, related_name='friends')
    from_user = models.ForeignKey(User, related_name='_unused_friend_relation')
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=1,default='F')
    objects = FriendshipManager()

    class Meta:
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')
        unique_together = ('from_user', 'to_user')

    
    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")
        super(Friend, self).save(*args, **kwargs)







# Create your models here.
