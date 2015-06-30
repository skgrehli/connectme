from django_cron import CronJobBase, Schedule
from ConnectMe.friendship.models import *



class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 1 MIN
	#RUN_AT_TIMES = ['6:30']
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'users.remove_friend_cronjob'    # a unique code

    def do(self):
    	print "goswami"

    	FriendshipRequest.remove_friend_cronjob()
        print "sandeep"    # do your thing here