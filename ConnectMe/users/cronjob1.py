from ConnectMe.friendship.models import *
from ConnectMe.users.models import *
import datetime
def my_scheduled_job():
	print "cornjob done",datetime.datetime.now()
  	FriendshipRequest.remove_friend_cronjob()
  	