from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseForbidden, HttpResponseRedirect, Http404)
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext as _

from forms import OrganizationForm
from models import Organization

from participe.challenge.models import Challenge, CHALLENGE_STATUS
from participe.core.user_tests import user_profile_completed


@login_required
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
def organization_create(request):
    if request.method == "POST":
        form = OrganizationForm(
                request.user, request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect("organization_list")
    else:
        form = OrganizationForm(
                request.user, request.POST or None, request.FILES or None)
    return render_to_response('organization_create.html',
            RequestContext(request, {'form': form}))
    
def organization_list(request):
    organizations = Organization.objects.all().filter(
            is_deleted=False).order_by("name")
    return render_to_response('organization_list.html',
            RequestContext(request, {
                    'organizations': organizations,
                    }))

def organization_detail(request, organization_id, slug=None):
    organization = get_object_or_404(Organization, pk=organization_id)
    if organization.is_deleted:
        raise Http404
    affiliated_users = organization.affiliated_users.all()
    upcoming_challenges = Challenge.objects.filter(
            organization=organization,
            status=CHALLENGE_STATUS.UPCOMING,
            is_deleted=False,
            )
    completed_challenges = Challenge.objects.filter(
            organization=organization,
            status=CHALLENGE_STATUS.COMPLETED,
            is_deleted=False,
            )
    return render_to_response('organization_detail.html',
            RequestContext(request, {
                    'organization': organization,
                    'affiliated_users': affiliated_users,
                    'upcoming_challenges': upcoming_challenges,
                    'completed_challenges': completed_challenges,
                    }))

def organization_iframe_upcoming(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    challenges_upcoming = Challenge.objects.filter(
            status=CHALLENGE_STATUS.UPCOMING,
            organization=organization,
            is_deleted=False
            ).order_by("created_at")
    return render_to_response('organization_iframe.html',
            RequestContext(request, {
                    'organization': organization,
                    'challenges_upcoming': challenges_upcoming,
                    }))

def organization_iframe_completed(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    challenges_completed = Challenge.objects.filter(
            status=CHALLENGE_STATUS.COMPLETED,
            organization=organization,
            is_deleted=False
            ).order_by("created_at")
    return render_to_response('organization_iframe.html',
            RequestContext(request, {
                    'organization': organization,
                    'challenges_completed': challenges_completed,
                    }))