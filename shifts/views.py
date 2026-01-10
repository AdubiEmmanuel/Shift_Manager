from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from users.models import User

from .forms import LeaveRequestForm
from .models import LeaveRequest


@login_required
def leave_create_view(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.requester = request.user
            leave.save()
            messages.success(request, "Leave request submitted.")
            return redirect("shifts:leave_list")
    else:
        form = LeaveRequestForm()
    return render(request, "shifts/leave_create.html", {"form": form})


@login_required
def leave_list_view(request):
    user = request.user
    if user.is_super_admin:
        qs = LeaveRequest.objects.all()
    elif user.is_line_manager:
        team = User.objects.filter(line_manager=user)
        qs = LeaveRequest.objects.filter(requester__in=team) | LeaveRequest.objects.filter(requester=user)
    else:
        qs = LeaveRequest.objects.filter(requester=user)
    qs = qs.order_by("-created_at")
    return render(request, "shifts/leave_list.html", {"leave_requests": qs})


@login_required
def approve_leave_view(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    user = request.user
    # Only superadmin or the requester's line manager may approve
    allowed = user.is_super_admin or (user.is_line_manager and leave.requester.line_manager_id == user.id)
    if not allowed:
        messages.error(request, "Not authorized to approve this leave.")
        return redirect("shifts:leave_list")

    action = request.POST.get("action")
    if action == "approve":
        leave.approve(user)
        messages.success(request, "Leave approved.")
    elif action == "reject":
        leave.reject(user)
        messages.success(request, "Leave rejected.")
    return redirect("shifts:leave_list")
