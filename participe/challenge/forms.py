# -*- coding: utf-8 -*-

import os
from datetime import datetime

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from models import Challenge, PARTICIPATION_STATE

import participe.core.html5_widgets as widgets

class CreateChallengeForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(CreateChallengeForm, self).__init__(*args, **kwargs)
        self.user = user

        if self.instance and self.instance.pk:
            pass

        organizations = self.user.organization_set.all().order_by("name")
        self.fields["organization"].required = False
        if organizations:
            #self.fields["organization"].empty_label = None
            self.fields["organization"].queryset = organizations
            self.fields["organization"].initial = organizations[0]
        else:
            #self.fields["organization"].required = False
            self.fields["organization"].widget = \
                self.fields["organization"].hidden_widget()

        """
        self.contact_choices = [
            ("me", "%s (%s)" % (self.user.get_full_name(), self.user.email)),
            ("he", _("Affiliate different person")), ]
        self.fields["contact"].choices = self.contact_choices
        self.fields["contact"].initial = "me"
        """

    contact = forms.TextInput()
    link = forms.TextInput()
    start_date = forms.DateField(
        input_formats=("%d.%m.%Y",),
        widget=forms.DateInput(
            format="%d.%m.%Y",
            attrs={"class": "input-small"}))
    start_time = forms.TimeField(
        input_formats=("%H:%M",),
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={"class": "input-mini"}))

    class Meta:
        model = Challenge
        fields = ["avatar", "name", "description", "location", "duration",
                  "contact", "link", "start_date", "start_time",
                  "organization"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": u"Ein sprechender Titel für dein Engagement",
                    "class": "input-xl"
                }),
            "location": forms.TextInput(
                attrs={"placeholder": "Wo findet dein Engagement statt? Wie kommt man dahin?",
                       "class": "input-xl"}),

            "duration": widgets.NumberInput(
                attrs={'min': '1', 'max': '999999', 'step': '1',
                       "class": "input-mini"}),

            "contact": forms.TextInput(
                attrs={"placeholder": "Wie können dich Menschen kontaktieren, welche mitmachen wollen?",
                       "class": "input-xl"}),

            "link": forms.TextInput(
                attrs={"placeholder": "Link zu weiteren Informationen zu deinem Engagement",
                       "class": "input-xl"}),
        }

    def clean_avatar(self):
        data = self.cleaned_data['avatar']

        if data:
            if settings.AVATAR_ALLOWED_FILE_EXTS:
                (root, ext) = os.path.splitext(data.name.lower())
                if ext not in settings.AVATAR_ALLOWED_FILE_EXTS:
                    raise forms.ValidationError(
                        "%(ext)s is an invalid file extension. "
                        "Authorized extensions are : %(valid_exts_list)s" %
                        {'ext': ext,
                         'valid_exts_list':
                             ", ".join(settings.AVATAR_ALLOWED_FILE_EXTS)})
            if data.size > settings.AVATAR_MAX_SIZE:
                raise forms.ValidationError(
                    u"Your file is too big (%(size)s), the maximum "
                    "allowed size is %(max_valid_size)s" %
                    {'size': filesizeformat(data.size),
                     'max_valid_size':
                         filesizeformat(settings.AVATAR_MAX_SIZE)})
        return self.cleaned_data['avatar']

    def clean_duration(self):
        if self.cleaned_data["duration"] < 1:
            raise forms.ValidationError(
                _("Value should be greater or equal 1"))
        return self.cleaned_data["duration"]

    def save(self, commit=True):
        instance = super(CreateChallengeForm, self).save(commit=False)
        instance.contact_person = self.user

        if commit:
            instance.save()


class EditChallengeForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(EditChallengeForm, self).__init__(*args, **kwargs)
        self.user = user

        self.fields.keyOrder = ["avatar", "name", "description", "location",
                                "duration", "contact", "link",
                                "start_date", "start_time",
                                "deleted_reason"]

    start_date = forms.DateField(
        input_formats=("%d.%m.%Y",),
        widget=forms.DateInput(
            format="%d.%m.%Y",
            attrs={"class": "input-small"}))

    class Meta:
        model = Challenge
        fields = ["avatar", "name", "description", "location", "duration",
                  "is_contact_person", "contact",
                  "link", "start_date", "start_time",
                  "deleted_reason"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "input-xl"
                }),
            "location": forms.TextInput(
                attrs={
                    "class": "input-xl"
                }),
            "duration": widgets.NumberInput(
                attrs={'min': '1', 'max': '100', 'step': '1',
                       "class": "input-mini"}),
            "contact": forms.TextInput(
                attrs={
                    "class": "input-xl"
                }),

            "link": widgets.URLInput(
                attrs={
                    "class": "input-xl"
                }),

            "start_time": widgets.TimeInput(
                attrs={"class": "input-large"}),

            "deleted_reason": forms.Textarea(
                attrs={"cols": 25, "rows": 5,
                       "placeholder": _("Reason for deletion "
                                        "(at least 20 symbols)")}),
        }

    def clean_duration(self):
        if self.cleaned_data["duration"] < 1:
            raise forms.ValidationError(
                _("Value should be greater or equal 1"))
        return self.cleaned_data["duration"]

