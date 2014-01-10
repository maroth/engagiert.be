# -*- coding: utf-8 -*-
from datetime import date
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from easy_thumbnails.fields import ThumbnailerImageField
from tinymce.models import HTMLField

from participe.organization.models import Organization
from participe.enum import enum


CHALLENGE_STATUS = enum(UPCOMING="0", COMPLETED="1")

challenge_status_choices = \
    [
        (CHALLENGE_STATUS.UPCOMING, _("Upcoming")),
        (CHALLENGE_STATUS.COMPLETED, _("Completed")),
    ]


class Challenge(models.Model):
    avatar = ThumbnailerImageField(
        upload_to='img/challenges', verbose_name=_("Avatar"))
    name = models.CharField(max_length=150, verbose_name="Ein sprechender Titel für das Engagement")
    description = HTMLField(verbose_name="Eine Beschreibung des Engagements")
    location = models.CharField(
        max_length=80, null=True, blank=True, verbose_name=_("Location"))
    duration = models.PositiveIntegerField(
        default=1, null=True, blank=True, verbose_name=_("Duration"))

    status = models.CharField(
        max_length=2, choices=challenge_status_choices,
        default=CHALLENGE_STATUS.UPCOMING,
        verbose_name=_("Status"))

    # Even if primary contact person isn't set, despite everything,
    # value 'contact_person' can be used to identify who has created challenge
    is_contact_person = models.BooleanField(default=True)
    contact_person = models.ForeignKey(
        User, related_name="contact_chl_set",
        verbose_name=_("Contact Person"))

    is_alt_person = models.BooleanField(default=False)
    contact = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_("Contact"))
    link = models.URLField(max_length=1000, null=True, blank=True, verbose_name=_("Link"))

    start_date = models.DateField(verbose_name=_("Start Date"))
    start_time = models.TimeField(verbose_name=_("Start Time"))

    organization = models.ForeignKey(
        Organization, null=True, blank=True,
        verbose_name=_("Organization"))

    is_deleted = models.BooleanField(default=False)
    deleted_reason = models.TextField(
        null=True, blank=True, verbose_name=_("Reason for deletion"))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('challenge')
        verbose_name_plural = _('challenges')
        ordering = ['name', ]

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        if self.organization:
            return reverse(
                'participe.challenge.views.challenge_detail',
                kwargs={
                    "challenge_id": str(self.id),
                    "org_slug": slugify(self.organization.name),
                    "chl_slug": slugify(self.name),
                })
        else:
            return reverse(
                'participe.challenge.views.challenge_detail',
                kwargs={
                    "challenge_id": str(self.id),
                    "chl_slug": slugify(self.name),
                })

    def get_full_url(self, request):
        url = u"http://{0}{1}".format(
            request.get_host(),
            self.get_absolute_url())
        return url

    def get_edit_url(self):
        return reverse(
            'participe.challenge.views.challenge_edit',
            args=[str(self.id)])

    def get_acknowledged_qs(self):
        """Returns participations with Acknowledged status"""
        return Participation.objects.filter(
            challenge=self,
            status=PARTICIPATION_STATE.ACKNOWLEDGED)

    @property
    def stat_status_name(self):
        for code, name in challenge_status_choices:
            if self.status == code:
                return name
        return ''

    @property
    def get_waiting_count(self):
        return Participation.objects.all().filter(
            challenge=self,
            status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION).count()

    @property
    def get_confirmed_count(self):
        return Participation.objects.all().filter(
            challenge=self,
            status=PARTICIPATION_STATE.CONFIRMED).count()

    @property
    def has_waiting_for_confirmation(self):
        if Participation.objects.filter(
                status=PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
                challenge=self):
            return True
        return False

    @property
    def has_waiting_for_acknowledgement(self):
        if Participation.objects.filter(
                status=PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT,
                challenge=self):
            return True
        return False

    @property
    def is_overdue(self):
        if self.start_date < date.today():
            return True
        return False


PARTICIPATION_REMOVE_MODE = enum(
    REMOVE_APPLICATION="0",
    REJECT_APPLICATION="1",
    REJECT_SELFREFLECTION="2",
    ACKNOWLEDGE="4",
)

PARTICIPATION_STATE = enum(
    WAITING_FOR_CONFIRMATION="0",
    CONFIRMATION_DENIED="1",
    CONFIRMED="2",
    CANCELLED_BY_ADMIN="3",
    CANCELLED_BY_USER="4",
    WAITING_FOR_SELFREFLECTION="5",
    WAITING_FOR_ACKNOWLEDGEMENT="6",
    ACKNOWLEDGED="7",
)

participation_status_choices = [
    (PARTICIPATION_STATE.WAITING_FOR_CONFIRMATION,
     _("Waiting for confirmation")),
    (PARTICIPATION_STATE.CONFIRMATION_DENIED,
     _("You were not accepted to this challenge")),
    (PARTICIPATION_STATE.CONFIRMED,
     _("Signed up")),
    (PARTICIPATION_STATE.CANCELLED_BY_ADMIN,
     _("The organizer removed you from this challenge")),
    (PARTICIPATION_STATE.CANCELLED_BY_USER,
     _("You withdrew your participation to this challenge")),
    (PARTICIPATION_STATE.WAITING_FOR_SELFREFLECTION,
     _("Please write your experience report")),
    (PARTICIPATION_STATE.WAITING_FOR_ACKNOWLEDGEMENT,
     _("Waiting for acknowledgement")),
    (PARTICIPATION_STATE.ACKNOWLEDGED,
     _("Report acknowledged")),
]


class Comment(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"))
    challenge = models.ForeignKey(Challenge, verbose_name=_("Challenge"))
    text = models.TextField(verbose_name=_("Text"))
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('commment')
        verbose_name_plural = _('comments')
        ordering = ['created_at', ]
