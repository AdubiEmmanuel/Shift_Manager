from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse

from shifts.models import LeaveRequest
from .models import User
from django.utils import timezone

from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse




def superadmin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_super_admin)(view_func)


@login_required
def dashboard(request):
    user = request.user
    if user.is_super_admin:
        return superadmin_dashboard(request)
    if user.is_line_manager:
        return line_manager_dashboard(request)
    return staff_dashboard(request)


@login_required
def superadmin_dashboard(request):
    total_users = User.objects.count()
    total_leaves = LeaveRequest.objects.count()
    pending_leaves = LeaveRequest.objects.filter(status=LeaveRequest.STATUS_PENDING).count()
    approved_leaves = LeaveRequest.objects.filter(status=LeaveRequest.STATUS_APPROVED).count()
    # prepare simple monthly counts for the last 6 months
    from django.utils import timezone
    import calendar
    from datetime import date

    now = timezone.now().date()
    months = []
    counts = []
    for offset in range(5, -1, -1):
        # compute year and month for the offset month
        month = now.month - offset
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        label = calendar.month_abbr[month]
        months.append(label)
        counts.append(LeaveRequest.objects.filter(created_at__gte=start, created_at__lt=end).count())

    # upcoming leaves (starting today or in future)
    upcoming_leaves_count = LeaveRequest.objects.filter(start_datetime__gte=timezone.now()).count()
    recent_leaves = LeaveRequest.objects.order_by("-created_at")[:6]

    context = {
        "total_users": total_users,
        "total_leaves": total_leaves,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "upcoming_leaves_count": upcoming_leaves_count,
        "recent_leaves": recent_leaves,
        "chart_months": months,
        "chart_counts": counts,
        "create_user_form": UserRegistrationForm(),
    }
    return render(request, "dashboards/superadmin_dashboard.html", context)



@superadmin_required
@require_http_methods(["POST"])
def create_user_ajax(request):
    # Expect AJAX POST with form data
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return JsonResponse({"success": False, "error": "AJAX only"}, status=400)
    form = UserRegistrationForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data.get("email")
        user.phone = form.cleaned_data.get("phone", "")
        user.save()
        return JsonResponse(
            {
                "success": True,
                "message": "User created",
                "user": {"id": user.pk, "username": user.username, "name": user.get_full_name()},
            }
        )
    else:
        errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
        return JsonResponse({"success": False, "errors": errors}, status=400)


@superadmin_required
def create_user_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email")
            user.phone = form.cleaned_data.get("phone", "")
            user.save()
            return redirect(reverse("users:dashboard"))
    else:
        form = UserRegistrationForm()
    return render(request, "users/create_user.html", {"form": form})


@superadmin_required
def user_list_view(request):
    users = User.objects.order_by("-date_joined")[:50]
    return render(request, "users/user_list.html", {"users": users})


@superadmin_required
@require_http_methods(["GET", "POST"])
def user_edit_view(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated.")
            return redirect(reverse("users:user_list"))
    else:
        form = UserUpdateForm(instance=user_obj)
    return render(request, "users/edit_user.html", {"form": form, "user_obj": user_obj})


@superadmin_required
@require_http_methods(["GET", "POST"])
def user_delete_view(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        # prevent deleting self
        if request.user.pk == user_obj.pk:
            messages.error(request, "You cannot delete your own account.")
            return redirect(reverse("users:user_list"))
        user_obj.delete()
        messages.success(request, "User deleted.")
        return redirect(reverse("users:user_list"))
    return render(request, "users/confirm_delete_user.html", {"user_obj": user_obj})


@login_required
def line_manager_dashboard(request):
    team = User.objects.filter(line_manager=request.user)
    team_leaves = LeaveRequest.objects.filter(requester__in=team).order_by("-created_at")
    # counts for the team
    team_total = team_leaves.count()
    team_pending = team_leaves.filter(status=LeaveRequest.STATUS_PENDING).count()
    team_approved = team_leaves.filter(status=LeaveRequest.STATUS_APPROVED).count()
    upcoming_leaves_count = team_leaves.filter(start_datetime__gte=timezone.now()).count()
    recent_leaves = team_leaves[:6]
    context = {
        "team": team,
        "team_leaves": team_leaves[:10],
        "total_leaves": team_total,
        "pending_leaves": team_pending,
        "approved_leaves": team_approved,
        "upcoming_leaves_count": upcoming_leaves_count,
        "recent_leaves": recent_leaves,
    }
    return render(request, "dashboards/manager_dashboard.html", context)


@login_required
def staff_dashboard(request):
    my_leaves = LeaveRequest.objects.filter(requester=request.user).order_by("-created_at")
    # show contacts (line manager and colleagues under same manager)
    line_manager = request.user.line_manager
    colleagues = User.objects.filter(line_manager=line_manager).exclude(pk=request.user.pk) if line_manager else User.objects.none()
    # user-specific counts
    total_leaves = my_leaves.count()
    pending_leaves = my_leaves.filter(status=LeaveRequest.STATUS_PENDING).count()
    approved_leaves = my_leaves.filter(status=LeaveRequest.STATUS_APPROVED).count()
    upcoming_leaves_count = my_leaves.filter(start_datetime__gte=timezone.now()).count()
    recent_leaves = my_leaves[:6]
    context = {
        "my_leaves": my_leaves,
        "line_manager": line_manager,
        "colleagues": colleagues,
        "total_leaves": total_leaves,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "upcoming_leaves_count": upcoming_leaves_count,
        "recent_leaves": recent_leaves,
    }
    return render(request, "dashboards/staff_dashboard.html", context)


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.phone = form.cleaned_data.get("phone", "")
            user.save()
            messages.success(request, "Account created. Please log in.")
            return redirect("users:login")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def home(request):
    return render(request, "landing.html")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("users:profile")
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, "users/profile.html", {"form": form})
