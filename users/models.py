from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_SUPERADMIN = "superadmin"
    ROLE_LINE_MANAGER = "line_manager"
    ROLE_STAFF = "staff"

    ROLE_CHOICES = [
        (ROLE_SUPERADMIN, "Super Admin"),
        (ROLE_LINE_MANAGER, "Line Manager"),
        (ROLE_STAFF, "Staff"),
    ]

    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=ROLE_STAFF)
    # Each staff may have a line manager (self-referential)
    line_manager = models.ForeignKey(
        "self", related_name="team_members", null=True, blank=True, on_delete=models.SET_NULL
    )
    phone = models.CharField(max_length=32, blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def is_super_admin(self):
        return self.role == self.ROLE_SUPERADMIN or self.is_superuser

    @property
    def is_line_manager(self):
        return self.role == self.ROLE_LINE_MANAGER

    @property
    def is_staff_user(self):
        return self.role == self.ROLE_STAFF

    def __str__(self):
        return self.get_full_name() or self.username
