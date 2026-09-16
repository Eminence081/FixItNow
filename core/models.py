from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Profile(models.Model):
    ROLE_CHOICES = [
        ("client", "Client"),
        ("provider", "Provider"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=80, blank=True)

    business_name = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

    @property
    def average_rating(self):
        reviews = Review.objects.filter(booking__service__provider=self.user)
        if not reviews.exists():
            return None
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def review_count(self):
        return Review.objects.filter(booking__service__provider=self.user).count()

    @property
    def completed_jobs(self):
        return Booking.objects.filter(
            service__provider=self.user, status="completed"
        ).count()


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(
        max_length=10, default="🔧", help_text="An emoji used as the category icon"
    )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="services"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="services"
    )
    title = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    city = models.CharField(max_length=80)
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("service_detail", args=[self.pk])

    @property
    def average_rating(self):
        reviews = Review.objects.filter(booking__service=self)
        if not reviews.exists():
            return None
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("declined", "Declined"),
        ("cancelled", "Cancelled"),
    ]

    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookings_made"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="bookings", null=True, blank=True
    )
    quote = models.ForeignKey(
        "Quote", on_delete=models.SET_NULL, related_name="booking", null=True, blank=True
    )
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    address = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.display_title} — {self.client.username} ({self.status})"

    @property
    def display_title(self):
        return self.service.title if self.service else (self.quote.request.title if self.quote else "Service request")

    @property
    def display_provider(self):
        return self.service.provider if self.service else (self.quote.provider if self.quote else None)

    @property
    def display_price(self):
        return self.service.price if self.service else (self.quote.price if self.quote else None)

    @property
    def has_review(self):
        return hasattr(self, "review")


class Review(models.Model):
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="review"
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    provider_reply = models.TextField(blank=True)
    provider_reply_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}★ for {self.booking.display_title}"


class SavedProvider(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_providers")
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_by_clients")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "provider")
        ordering = ["-created_at"]


class ServiceRequest(models.Model):
    URGENCY_CHOICES = [("low", "Low"), ("medium", "Medium"), ("high", "High")]
    STATUS_CHOICES = [("open", "Open"), ("closed", "Closed")]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="service_requests")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="service_requests")
    title = models.CharField(max_length=120)
    description = models.TextField()
    budget_range = models.CharField(max_length=60, blank=True)
    city = models.CharField(max_length=80)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default="medium")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Quote(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="quotes")
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quotes_submitted")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
