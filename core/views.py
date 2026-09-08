from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm, ProfileForm, RegisterForm, ReviewForm, ServiceForm
from .models import Booking, Category, Profile, Review, Service


def home(request):
    categories = Category.objects.all()
    featured = Service.objects.filter(is_active=True).select_related(
        "provider", "category"
    )[:6]
    context = {
        "categories": categories,
        "featured": featured,
        "provider_count": Profile.objects.filter(role="provider").count(),
        "service_count": Service.objects.filter(is_active=True).count(),
        "completed_count": Booking.objects.filter(status="completed").count(),
    }
    return render(request, "core/home.html", context)


def browse_services(request):
    services = Service.objects.filter(is_active=True).select_related(
        "provider", "category"
    )

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    city = request.GET.get("city", "").strip()
    provider_id = request.GET.get("provider", "")

    if query:
        services = services.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        services = services.filter(category__slug=category_slug)
    if city:
        services = services.filter(city__icontains=city)
    if provider_id:
        services = services.filter(provider_id=provider_id)

    paginator = Paginator(services, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "query": query,
        "selected_category": category_slug,
        "city": city,
        "provider_id": provider_id,
        "provider_filter": services.first().provider if provider_id and services.exists() else None,
    }
    return render(request, "core/browse.html", context)


def service_detail(request, pk):
    service = get_object_or_404(
        Service.objects.select_related("provider", "category"), pk=pk
    )
    provider_profile = get_object_or_404(Profile, user=service.provider)
    reviews = Review.objects.filter(booking__service=service).select_related(
        "booking__client"
    )
    other_services = Service.objects.filter(
        provider=service.provider, is_active=True
    ).exclude(pk=service.pk)

    context = {
        "service": service,
        "provider_profile": provider_profile,
        "reviews": reviews,
        "other_services": other_services,
    }
    return render(request, "core/service_detail.html", context)


def provider_list(request):
    providers = Profile.objects.filter(role="provider", is_approved=True).select_related("user")
    return render(request, "core/providers.html", {"providers": providers})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                role=form.cleaned_data["role"],
                city=form.cleaned_data["city"],
                phone=form.cleaned_data.get("phone", ""),
            )
            login(request, user)
            messages.success(request, "Welcome to FixItNow! Your account is ready.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "core/register.html", {"form": form})


@login_required
def dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role == "provider":
        bookings = Booking.objects.filter(service__provider=request.user).select_related(
            "service", "client"
        )
        services = Service.objects.filter(provider=request.user)
        return render(
            request,
            "core/dashboard_provider.html",
            {"profile": profile, "bookings": bookings, "services": services},
        )
    else:
        bookings = Booking.objects.filter(client=request.user).select_related(
            "service", "service__provider"
        )
        return render(
            request,
            "core/dashboard_client.html",
            {"profile": profile, "bookings": bookings},
        )


@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "core/edit_profile.html", {"form": form, "profile": profile})


@login_required
def add_service(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != "provider":
        messages.error(request, "Only providers can list services.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.city = service.city or profile.city
            service.save()
            messages.success(request, "Service listed.")
            return redirect("dashboard")
    else:
        form = ServiceForm(initial={"city": profile.city})
    return render(request, "core/service_form.html", {"form": form, "title": "List a new service"})


@login_required
def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated.")
            return redirect("dashboard")
    else:
        form = ServiceForm(instance=service)
    return render(request, "core/service_form.html", {"form": form, "title": "Edit service"})


@login_required
def book_service(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role == "provider":
        messages.error(request, "Provider accounts can't book services. Register a client account.")
        return redirect("service_detail", pk=pk)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.service = service
            booking.save()
            messages.success(request, "Booking request sent! The provider will confirm shortly.")
            return redirect("dashboard")
    else:
        form = BookingForm()
    return render(request, "core/book_service.html", {"form": form, "service": service})


@login_required
def update_booking_status(request, pk, status):
    booking = get_object_or_404(Booking, pk=pk, service__provider=request.user)
    valid_transitions = {
        "confirmed": ["pending"],
        "declined": ["pending"],
        "completed": ["confirmed"],
    }
    if status in valid_transitions and booking.status in valid_transitions[status]:
        booking.status = status
        booking.save()
        messages.success(request, f"Booking marked as {status}.")
    else:
        messages.error(request, "That status change isn't allowed.")
    return redirect("dashboard")


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    if booking.status in ["pending", "confirmed"]:
        booking.status = "cancelled"
        booking.save()
        messages.success(request, "Booking cancelled.")
    return redirect("dashboard")


@login_required
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == "POST":
        title = service.title
        service.delete()
        messages.success(request, f'"{title}" has been deleted.')
        return redirect("dashboard")
    return render(request, "core/confirm_delete.html", {
        "object_label": service.title,
        "object_type": "service",
        "cancel_url": "dashboard",
    })


@login_required
def delete_booking_record(request, pk):
    # Clients can permanently remove a booking record once it's no longer
    # active (cancelled, declined, or completed) — this is a real delete,
    # separate from cancel_booking which only changes status.
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    if booking.status not in ["cancelled", "declined", "completed"]:
        messages.error(request, "Only finished or cancelled bookings can be deleted.")
        return redirect("dashboard")
    if request.method == "POST":
        label = booking.service.title
        booking.delete()
        messages.success(request, f'Booking record for "{label}" deleted.')
        return redirect("dashboard")
    return render(request, "core/confirm_delete.html", {
        "object_label": booking.service.title,
        "object_type": "booking record",
        "cancel_url": "dashboard",
    })


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, booking__client=request.user)
    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted.")
        return redirect("dashboard")
    return render(request, "core/confirm_delete.html", {
        "object_label": f"your review of {review.booking.service.title}",
        "object_type": "review",
        "cancel_url": "dashboard",
    })


@login_required
def leave_review(request, pk):
    booking = get_object_or_404(
        Booking, pk=pk, client=request.user, status="completed"
    )
    if hasattr(booking, "review"):
        messages.info(request, "You've already reviewed this booking.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            messages.success(request, "Thanks for your review!")
            return redirect("dashboard")
    else:
        form = ReviewForm()
    return render(request, "core/leave_review.html", {"form": form, "booking": booking})