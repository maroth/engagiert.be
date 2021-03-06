from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
    # i18n
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^about/', include('django.contrib.flatpages.urls')),

    # Home
    url(r'^$', 'django.views.generic.simple.direct_to_template',
            {'template': 'home.html'}, name='home'),
    url(r'^home/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'home.html'}, name='home'),

    url(r'', include('social_auth.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^tinymce/', include('tinymce.urls')),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    )

urlpatterns += patterns('participe.account.views',
    # Account
    url(r'^accounts/login/$', 'account_login', name='login'),
    url(r'^accounts/logout/$', 'account_logout', {"next_page": "/"}, name='logout'),
    url(r'^accounts/signup/$', 'signup', name='signup'),
    url(r'^accounts/profile/view/$', 'view_myprofile', name='view_myprofile'),
    url(r'^accounts/profile/view/(?P<user_id>[\w_-]+)/$', 'view_profile',
            name='view_profile'),
    url(r'^accounts/profile/edit/$', 'edit_profile', name='edit_profile'),
    url(r'^accounts/profile/delete/$', 'delete_profile', name='delete_profile'),
    url(r'^accounts/password/reset/$', 'reset_password', name='reset_password'),
    url(r'^accounts/password/renew/$', 'notify_forgotten_password', name='notify_forgotten_password'),
    url(r'^accounts/password/renew/(?P<uidb36>[0-9A-Za-z]{1,13})-'
            '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            'renew_forgotten_password',
            name='renew_forgotten_password'),

    url(r'^account/confirmation/(?P<confirmation_code>[0-9a-zA-Z-_:]+)/$',
            'email_confirmation',
            name='email_confirmation'),

    # TODO On general success move this to separate application
    url(r'^accounts/avatar/add$', 'change_avatar', name='add_avatar'),
    url(r'^accounts/avatar/change$', 'change_avatar', name='change_avatar'),
    url(r'^accounts/avatar/crop$', 'crop_avatar', name='crop_avatar'),
    )

urlpatterns += patterns('participe.challenge.views',
    # Challenge
    url(r'^challenges/$', 'challenge_list', name='challenge_list'),
    url(r'^challenges/create/$', 'challenge_create', name='challenge_create'),

    url(r'^challenges/(?P<challenge_id>\d+)/(?P<chl_slug>[\w_-]+)/$', 'challenge_detail', name='challenge_detail'),
    url(r'^challenges/(?P<challenge_id>\d+)/(?P<org_slug>[\w_-]+)/(?P<chl_slug>[\w_-]+)/$','challenge_detail', name='challenge_detail'),

    url(r'^challenges/edit/(?P<challenge_id>\d+)/$', 'challenge_edit',
            name='challenge_edit'),
    url(r'^challenges/comment/add/$', 'comment_add',
            name='comment_add'),
    url(r'^challenges/comment/delete/(?P<comment_id>\d+)/$', 'comment_delete',
            name='comment_delete'),
    )

urlpatterns += patterns('participe.organization.views',
    # Organization
    url(r'^organizations/$', 'organization_list', name='organization_list'),
    url(r'^organizations/create/$', 'organization_create',
            name='organization_create'),

    url(r'^organizations/(?P<organization_id>\d+)/(?P<slug>[\w_-]+)/$',
            'organization_detail', name='organization_detail'),

    url(r'^organizations/iframe/upcoming/(?P<organization_id>\d+)/$',
            'organization_iframe_upcoming',
            name='organization_iframe_upcoming'),
    url(r'^organizations/iframe/completed/(?P<organization_id>\d+)/$',
            'organization_iframe_completed',
            name='organization_iframe_completed'),
    )

# The big, fat disclaimer
# Using this method is inefficient and insecure.
# Do not use this in a production setting. Use this only for development.
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )