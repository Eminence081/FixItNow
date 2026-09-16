from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    BookingForm,
    ProfileForm,
    QuoteForm,
    RegisterForm,
    ReviewForm,
    ReviewReplyForm,
    ServiceForm,
    ServiceRequestForm,
)
from .models import (
    Booking,
    Category,
    Profile,
    Quote,
    Review,
    SavedProvider,
    Service,
    ServiceRequest,
)


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
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(category__slug__icontains=query)
        )
    if category_slug:
        services = services.filter(category__slug=category_slug)
    if city:
        services = services.filter(city__icontains=city)
    if provider_id:
        services = services.filter(provider_id=provider_id)

    paginator = Paginator(services, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    provider_profile = None
    if provider_id:
        provider_profile = get_object_or_404(
            Profile.objects.select_related("user"),
            user_id=provider_id,
            role="provider",
        )

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "query": query,
        "selected_category": category_slug,
        "city": city,
        "provider_id": provider_id,
        "provider_profile": provider_profile,
    }
    return render(request, "core/browse.html", context)


def service_detail(request, pk):
    service = get_object_or_404(
        Service.objects.select_related("provider", "category"), pk=pk
    )
    provider_profile = get_object_or_404(Profile, user=service.provider)
    reviews = Review.objects.filter(booking__service=service).select_related("booking__client")
    other_services = Service.objects.filter(
        provider=service.provider, is_active=True
    ).exclude(pk=service.pk)

    context = {
        "service": service,
        "provider_profile": provider_profile,
        "reviews": reviews,
        "other_services": other_services,
        "reply_form": ReviewReplyForm(),
        "can_reply": request.user.is_authenticated and request.user == service.provider,
    }
    return render(request, "core/service_detail.html", context)


def provider_saved_ids(request):
    if not request.user.is_authenticated:
        return set()
    try:
        if request.user.profile.role != "client":
            return set()
    except Profile.DoesNotExist:
        return set()
    return set(
        SavedProvider.objects.filter(client=request.user).values_list(
            "provider_id", flat=True
        )
    )


def provider_list(request):
    providers = Profile.objects.filter(role="provider", is_approved=True).select_related("user")

    query = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()

    if query:
        providers = providers.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(business_name__icontains=query)
            | Q(bio__icontains=query)
        )
    if city:
        providers = providers.filter(city__icontains=city)

    return render(request, "core/providers.html", {
        "providers": providers,
        "query": query,
        "city": city,
        "saved_provider_ids": provider_saved_ids(request),
    })


def provider_detail(request, pk):
    provider_user = get_object_or_404(User, pk=pk)
    provider_profile = get_object_or_404(
        Profile.objects.select_related("user"),
        user=provider_user,
        role="provider",
        is_approved=True,
    )
    services = Service.objects.filter(provider=provider_user, is_active=True).select_related(
        "category"
    )
    reviews = Review.objects.filter(booking__service__provider=provider_user).select_related(
        "booking__client", "booking__service"
    )
    return render(
        request,
        "core/provider_detail.html",
        {
            "provider_profile": provider_profile,
            "services": services,
            "reviews": reviews,
        },
    )


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile_data = {
                "user": user,
                "role": form.cleaned_data["role"],
                "city": form.cleaned_data["city"],
                "phone": form.cleaned_data.get("phone", ""),
            }
            if profile_data["role"] == "provider":
                profile_data.update({
                    "business_name": form.cleaned_data.get("business_name", ""),
                    "bio": form.cleaned_data.get("bio", ""),
                    "years_experience": form.cleaned_data.get("years_experience") or 0,
                    "is_available": form.cleaned_data.get("is_available", True),
                })
            Profile.objects.create(**profile_data)
            login(request, user)
            messages.success(request, "Welcome to FixItNow! Your account is ready.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "core/register.html", {"form": form})


@login_required
def post_login_redirect(request):
    if request.user.is_staff:
        return redirect("admin_analytics")
    return redirect("dashboard")


@login_required
def dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role == "provider":
        bookings = Booking.objects.filter(
            Q(service__provider=request.user) | Q(quote__provider=request.user)
        ).select_related(
            "service", "quote__request", "quote", "client"
        )
        services = Service.objects.filter(provider=request.user)
        reviews = Review.objects.filter(
            Q(booking__service__provider=request.user)
            | Q(booking__quote__provider=request.user)
        ).select_related("booking__client", "booking__service", "booking__quote__request")
        return render(
            request,
            "core/dashboard_provider.html",
            {"profile": profile, "bookings": bookings, "services": services, "reviews": reviews},
        )
    else:
        bookings = Booking.objects.filter(client=request.user).select_related(
            "service", "service__provider", "quote__provider", "quote__provider__profile", "quote__request"
        )
        saved_providers = SavedProvider.objects.filter(client=request.user).select_related("provider")
        return render(
            request,
            "core/dashboard_client.html",
            {"profile": profile, "bookings": bookings, "saved_providers": saved_providers},
        )


@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "core/edit_profile.html", {"form": form, "profile": profile})


@login_required
def toggle_availability(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    profile = get_object_or_404(Profile, user=request.user)
    profile.is_available = not profile.is_available
    profile.save(update_fields=["is_available"])
    state = "available" if profile.is_available else "busy"
    messages.success(request, f"You're now marked as {state}.")
    return redirect("dashboard")


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
        label = booking.display_title
        booking.delete()
        messages.success(request, f'Booking record for "{label}" deleted.')
        return redirect("dashboard")
    return render(request, "core/confirm_delete.html", {
        "object_label": booking.display_title,
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
        "object_label": f"your review of {review.booking.display_title}",
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


@login_required
def reply_to_review(request, pk):
    review = get_object_or_404(
        Review.objects.filter(
            Q(booking__service__provider=request.user)
            | Q(booking__quote__provider=request.user)
        ),
        pk=pk,
    )
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    form = ReviewReplyForm(request.POST, instance=review)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.provider_reply_at = timezone.now()
        reply.save(update_fields=["provider_reply", "provider_reply_at"])
        messages.success(request, "Your reply was saved.")
    return redirect("dashboard")


@login_required
def toggle_save_provider(request, provider_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != "client":
        messages.error(request, "Only clients can save providers.")
        return redirect("provider_list")
    provider = get_object_or_404(User, pk=provider_id)
    saved, created = SavedProvider.objects.get_or_create(client=request.user, provider=provider)
    if not created:
        saved.delete()
        messages.success(request, "Provider removed from saved providers.")
    else:
        messages.success(request, "Provider saved.")
    return redirect(request.META.get("HTTP_REFERER") or "provider_list")


@login_required
def post_request(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != "client":
        messages.error(request, "Only clients can post service requests.")
        return redirect("dashboard")
    if request.method == "POST":
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.client = request.user
            service_request.save()
            messages.success(request, "Your service request is now open for quotes.")
            return redirect("request_detail", pk=service_request.pk)
    else:
        form = ServiceRequestForm(initial={"city": profile.city})
    return render(request, "core/request_form.html", {"form": form})


def browse_requests(request):
    requests = ServiceRequest.objects.filter(status="open").select_related("client", "category")
    category_slug = request.GET.get("category", "")
    city = request.GET.get("city", "").strip()
    if category_slug:
        requests = requests.filter(category__slug=category_slug)
    if city:
        requests = requests.filter(city__icontains=city)
    return render(request, "core/browse_requests.html", {
        "requests": requests,
        "categories": Category.objects.all(),
        "selected_category": category_slug,
        "city": city,
    })


@login_required
def submit_quote(request, pk):
    profile = get_object_or_404(Profile, user=request.user)
    service_request = get_object_or_404(ServiceRequest, pk=pk, status="open")
    if profile.role != "provider":
        messages.error(request, "Only providers can submit quotes.")
        return redirect("request_detail", pk=pk)
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.request = service_request
            quote.provider = request.user
            quote.save()
            messages.success(request, "Your quote was submitted.")
            return redirect("request_detail", pk=pk)
    else:
        form = QuoteForm()
    return render(request, "core/quote_form.html", {"form": form, "service_request": service_request})


def request_detail(request, pk):
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related("client", "category"), pk=pk
    )
    quotes = service_request.quotes.select_related("provider", "provider__profile")
    can_quote = False
    can_accept_quote = request.user.is_authenticated and request.user == service_request.client
    if request.user.is_authenticated:
        try:
            can_quote = request.user.profile.role == "provider" and service_request.status == "open"
        except Profile.DoesNotExist:
            pass
    return render(request, "core/request_detail.html", {
        "service_request": service_request,
        "quotes": quotes,
        "can_quote": can_quote,
        "can_accept_quote": can_accept_quote,
    })


@login_required
def accept_quote(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    quote = get_object_or_404(Quote, pk=pk, request__client=request.user)
    if quote.request.status != "open":
        messages.error(request, "This service request is already closed.")
        return redirect("request_detail", pk=quote.request.pk)

    quote.accepted = True
    quote.save(update_fields=["accepted"])
    quote.request.status = "closed"
    quote.request.save(update_fields=["status"])
    Booking.objects.create(
        client=request.user,
        quote=quote,
        service=None,
        address="",
        status="confirmed",
    )
    messages.success(
        request,
        "Quote accepted! You can now contact the provider directly to arrange scheduling.",
    )
    return redirect("request_detail", pk=quote.request.pk)


@login_required
def admin_analytics(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to view analytics.")
        return redirect("home")
    users = User.objects.count()
    providers = Profile.objects.filter(role="provider").count()
    clients = Profile.objects.filter(role="client").count()
    services = Service.objects.count()
    active_services = Service.objects.filter(is_active=True).count()
    inactive_services = services - active_services
    bookings_by_status = list(
        Booking.objects.values("status").annotate(total=Count("id")).order_by("status")
    )
    review_summary = Review.objects.aggregate(total=Count("id"), average=Avg("rating"))
    recent_bookings = Booking.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    max_bookings = max((item["total"] for item in bookings_by_status), default=1)
    return render(request, "core/admin_analytics.html", {
        "users": users,
        "providers": providers,
        "clients": clients,
        "services": services,
        "active_services": active_services,
        "inactive_services": inactive_services,
        "bookings_by_status": bookings_by_status,
        "review_total": review_summary["total"] or 0,
        "average_rating": review_summary["average"],
        "recent_bookings": recent_bookings,
        "max_bookings": max_bookings,
    })