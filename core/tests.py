from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Booking, Category, Profile, Review, Service


class BrowseProviderFilterTests(TestCase):
    def setUp(self):
        self.provider_user = User.objects.create_user(
            username="providerone",
            email="provider@example.com",
            password="demo12345",
        )

        self.provider_profile = Profile.objects.create(
            user=self.provider_user,
            role="provider",
            city="Lagos",
            phone="08000000000",
            business_name="Fix Teams",
            bio="Professional service provider",
            years_experience=3,
            is_approved=True,
        )

        self.category = Category.objects.create(
            name="Plumbing",
            slug="plumbing",
            icon="🔧",
        )

        self.service = Service.objects.create(
            provider=self.provider_user,
            category=self.category,
            title="Pipe repair",
            description="Repair pipes quickly.",
            price=Decimal("25000"),
            duration_minutes=60,
            city="Lagos",
            is_active=True,
        )

    def test_browse_services_provider_filter_exposes_provider_profile(self):
        response = self.client.get(
            reverse("browse_services"),
            {"provider": self.provider_user.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("provider_profile", response.context)
        self.assertEqual(response.context["provider_profile"], self.provider_profile)
        self.assertContains(response, "Services by Fix Teams")

    def test_browse_services_search_matches_category_name_and_slug(self):
        for query in ["Plumbing", "plumbing"]:
            response = self.client.get(reverse("browse_services"), {"q": query})

            self.assertEqual(response.status_code, 200)
            self.assertIn(self.service, response.context["page_obj"].object_list)


class ProviderDirectoryTests(TestCase):
    def setUp(self):
        self.provider_user = User.objects.create_user(
            username="profdetail",
            email="detail@example.com",
            password="demo12345",
        )
        self.provider_profile = Profile.objects.create(
            user=self.provider_user,
            role="provider",
            city="Abuja",
            phone="07000000000",
            business_name="Prime Fix",
            bio="Trusted local technician",
            years_experience=4,
            is_approved=True,
        )
        self.category = Category.objects.create(
            name="Electrical",
            slug="electrical",
            icon="⚡",
        )
        self.service = Service.objects.create(
            provider=self.provider_user,
            category=self.category,
            title="Wiring check",
            description="Electrical safety check.",
            price=Decimal("35000"),
            duration_minutes=90,
            city="Abuja",
            is_active=True,
        )

        self.other_user = User.objects.create_user(
            username="otherprovider",
            email="other@example.com",
            password="demo12345",
        )
        self.other_profile = Profile.objects.create(
            user=self.other_user,
            role="provider",
            city="Lagos",
            phone="08000000000",
            business_name="CleanComet",
            bio="Cleaning and fixing services",
            years_experience=2,
            is_approved=True,
        )

    def test_provider_list_supports_search_and_city_filters(self):
        response = self.client.get(
            reverse("provider_list"),
            {"q": "Prime", "city": "Abuja"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["providers"]), [self.provider_profile])
        self.assertContains(response, "Prime Fix")
        self.assertNotContains(response, "CleanComet")

    def test_provider_detail_page_returns_provider_and_services(self):
        response = self.client.get(
            reverse("provider_detail", args=[self.provider_user.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["provider_profile"], self.provider_profile)
        self.assertIn(self.service, response.context["services"])
        self.assertContains(response, "Prime Fix")

    def test_service_detail_shows_callable_provider_phone(self):
        response = self.client.get(reverse("service_detail", args=[self.service.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="tel:07000000000"')
        self.assertContains(response, "Call provider: 07000000000")
