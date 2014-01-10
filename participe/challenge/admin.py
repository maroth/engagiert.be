from django.contrib import admin

from participe.challenge.models import Challenge, Comment


class ChallengeAdmin(admin.ModelAdmin):
    list_display = [
            "pk", "name", "status", "start_date", "organization",
            "contact_person", "is_deleted"]
    list_filter = [
            "name", "status", "start_date", "organization"]
    search_fields = [
            "name", "organization",]

class CommentAdmin(admin.ModelAdmin):
    list_display = ["pk", "user", "challenge", "text", "is_deleted",]
    list_filter = ["user", "challenge",]
    search_fields = ["user", "challenge",]


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Comment, CommentAdmin)
