from django.conf import settings
from django.db import models
from django.utils import timezone

class Holiday(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class CoverageAvailability(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coverage_availabilities"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} available {self.start_date} -> {self.end_date}"


class LeaveRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests"
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="approved_leaves",
        on_delete=models.SET_NULL,
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def approve(self, approver):
        self.status = self.STATUS_APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()

    def reject(self, approver):
        self.status = self.STATUS_REJECTED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()

    def cancel(self):
        self.status = self.STATUS_CANCELLED
        self.save()

    def __str__(self):
        return f"LeaveRequest({self.requester}, {self.start_datetime} -> {self.end_datetime})"


class CoverOffer(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, related_name="offers", on_delete=models.CASCADE)
    offered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cover_offers"
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def accept(self):
        self.accepted = True
        self.accepted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Offer({self.offered_by} for {self.leave_request})"


class LeaveRelieverAssignment(models.Model):
    leave_request = models.OneToOneField(
        LeaveRequest, related_name="reliever_assignment", on_delete=models.CASCADE
    )
    reliever = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="assigned_relievers",
        on_delete=models.SET_NULL,
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    via_offer = models.ForeignKey(CoverOffer, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Assignment({self.reliever} -> {self.leave_request})"
