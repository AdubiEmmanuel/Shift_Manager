from django.contrib import admin

from . import models

@admin.register(models.Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_recurring")
    list_filter = ("is_recurring",)


@admin.register(models.CoverageAvailability)
class CoverageAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("user", "start_date", "end_date", "created_at")
    search_fields = ("user__username",)


@admin.register(models.LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("requester", "start_datetime", "end_datetime", "status", "approved_by")
    list_filter = ("status",)
    search_fields = ("requester__username",)


@admin.register(models.CoverOffer)
class CoverOfferAdmin(admin.ModelAdmin):
    list_display = ("leave_request", "offered_by", "accepted", "created_at")
    list_filter = ("accepted",)


@admin.register(models.LeaveRelieverAssignment)
class LeaveRelieverAssignmentAdmin(admin.ModelAdmin):
    list_display = ("leave_request", "reliever", "assigned_by", "assigned_at")
