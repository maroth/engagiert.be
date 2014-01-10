from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from datetime import date

from forms import CreateChallengeForm, EditChallengeForm
from models import (Challenge, Comment, CHALLENGE_STATUS, PARTICIPATION_STATE, PARTICIPATION_REMOVE_MODE)

from participe.account.models import PRIVACY_MODE
from participe.account.utils import is_challenge_admin
from participe.core.decorators import challenge_admin
from participe.core.http import Http501
from participe.core.user_tests import user_profile_completed


@login_required
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
def challenge_create(request):
    form = CreateChallengeForm(
        request.user, request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("challenge_list")

    return render_to_response('challenge_create.html',
                              RequestContext(request, {'form': form}))


def challenge_list(request):
    challenges = Challenge.objects.all().filter(
        status=CHALLENGE_STATUS.UPCOMING,
        start_date__gte=date.today(),
        is_deleted=False)
    return render_to_response('challenge_list.html',
                              RequestContext(request, {
                                  'challenges': challenges,
                              }))


def challenge_detail(request, challenge_id, org_slug=None, chl_slug=None):
    ctx = {}

    user = request.user
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    ctx.update({"challenge": challenge})

    if challenge.is_deleted:
        return render_to_response('challenge_deleted_info.html',
                                  RequestContext(request, {
                                      "challenge": challenge,
                                      "subject": _("%(challenge_name)s was cancelled")
                                                 % {"challenge_name": challenge.name},
                                  }))

    if request.user.is_authenticated():
        ctx.update({"is_admin": is_challenge_admin(user, challenge)})

    # Extract comments
    comments = Comment.objects.all().filter(
        Q(challenge=challenge) & Q(is_deleted=False)
    ).order_by("created_at")
    ctx.update({"comments": comments})

    ctx.update({"PARTICIPATION_STATE": PARTICIPATION_STATE})
    ctx.update({"CHALLENGE_STATUS": CHALLENGE_STATUS})
    ctx.update({"PRIVACY_MODE": PRIVACY_MODE})
    ctx.update({"PARTICIPATION_REMOVE_MODE": PARTICIPATION_REMOVE_MODE})

    return render_to_response('challenge_detail.html',
                              RequestContext(request, ctx))


@login_required
@challenge_admin
@user_passes_test(user_profile_completed, login_url="/accounts/profile/edit/")
def challenge_edit(request, challenge_id):
    user = request.user
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if challenge.status == CHALLENGE_STATUS.COMPLETED:
        raise Http501

    form = EditChallengeForm(
        user,
        request.POST or None,
        request.FILES or None,
        instance=challenge)

    #save button clicked
    if request.method == "POST":
        if form.is_valid():
            form.save()

            if "delete" in request.POST:
                challenge.is_deleted = True
                challenge.save()

            return redirect("challenge_list")

    return render_to_response('challenge_edit.html', RequestContext(request, {'form': form}))


@login_required
@challenge_admin
def challenge_complete(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    if request.method == "POST":
        description = request.POST["description"]
        challenge.description = description
        challenge.status = CHALLENGE_STATUS.COMPLETED
        challenge.save()

        return redirect(challenge.get_absolute_url())
    return redirect("challenge_list")

@login_required
def comment_add(request):
    if request.method == "POST":
        challenge_id = request.POST.get('challenge_id', '')
        comment_text = request.POST.get('comment', '')

        challenge = get_object_or_404(Challenge, pk=challenge_id)
        comment = Comment.objects.create(
            user=request.user,
            challenge=challenge,
            text=comment_text,
        )
        comment.save()
        return redirect(challenge.get_absolute_url())
    return redirect("challenge_list")


@login_required
@challenge_admin
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_deleted = True
    comment.save()
    return redirect(comment.challenge.get_absolute_url())
