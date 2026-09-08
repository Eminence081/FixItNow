from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm, ProfileForm, RegisterForm, ReviewForm, ServiceForm
from .models import Booking, Category, Profile, Review, Service


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