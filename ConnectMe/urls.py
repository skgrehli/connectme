"""ConnectMe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns,include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
import django_cron

urlpatterns = patterns('',
    #url(r'', include('registration.backends.default.urls')),
    url(r'', include('django.contrib.auth.urls')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^friend_accept/','ConnectMe.friendship.views.friend_accept',name='friend_accept'),
    url(r'^find_friend/', 'ConnectMe.users.views.find_friend', name='find_friend'),
    url(r'^friend_list/', 'ConnectMe.friendship.views.friend_list', name='friend_list'),
    url(r'^invite_friends/','ConnectMe.friendship.views.invite_friends',name='invite_friends'),
    url(r'^$', 'ConnectMe.core.views.home', name='home'),
    #url(r"^login/$","ConnectMe.users.views.login_maybe_remember",name="login"),
    url(r'^login', 'ConnectMe.users.views.login', {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^reset/$', 'ConnectMe.users.views.reset', name='reset'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'ConnectMe.users.views.reset_confirm', name='password_reset_confirm'),
    url(r'^success/$', 'ConnectMe.users.views.success', name='success'),
    url(r'^signup/$', 'ConnectMe.users.views.signup', name='signup'),
    url(r'^settings/$', 'ConnectMe.core.views.settings', name='settings'),
    url(r'^settings/picture/$', 'ConnectMe.core.views.picture', name='picture'),
    url(r'^settings/change/$', 'ConnectMe.core.views.change', name='change'),
    url(r'^settings/upload_picture/$', 'ConnectMe.core.views.upload_picture', name='upload_picture'),
    url(r'^settings/save_uploaded_picture/$', 'ConnectMe.core.views.save_uploaded_picture', name='save_uploaded_picture'),
    url(r'^settings/password/$', 'ConnectMe.core.views.password', name='password'),
    url(r'^feeds/', include('ConnectMe.feeds.urls')),
    url(r'^(?P<username>[^/]+)/$', 'ConnectMe.core.views.profile', name='profile'),
    url(r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),
    )+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
