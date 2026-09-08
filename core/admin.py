from django.contrib import admin
from .models import Profile, Category, Service, Booking, Review


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "city", "is_approved")
    list_filter = ("role", "is_approved", "city")
    search_fields = ("user__username", "business_name")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "provider", "category", "price", "city", "is_active")
    list_filter = ("category", "city", "is_active")
    search_fields = ("title", "provider__username")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("service", "client", "scheduled_date", "status")
    list_filter = ("status", "scheduled_date")
    search_fields = ("service__title", "client__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "rating", "created_at")
