import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from core.models import Booking, Category, Profile, Review, Service


class Command(BaseCommand):
    help = "Seed the database with demo data for FixItNow"

    def handle(self, *args, **kwargs):
        categories_data = [
            ("Plumbing", "plumbing", "🔧"),
            ("Electrical", "electrical", "💡"),
            ("Cleaning", "cleaning", "🧹"),
            ("Moving", "moving", "📦"),
            ("Painting", "painting", "🎨"),
            ("Appliance Repair", "appliance-repair", "🔌"),
            ("Gardening", "gardening", "🌿"),
            ("Carpentry", "carpentry", "🪚"),
        ]
        categories = {}
        for name, slug, icon in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=slug, defaults={"name": name, "icon": icon}
            )
            categories[slug] = cat
        self.stdout.write(self.style.SUCCESS(f"Categories: {Category.objects.count()}"))

        providers_data = [
            ("tunde", "Tunde", "Adebayo", "Adebayo Plumbing Services", "plumbing",
             "Licensed plumber with 8 years fixing leaks, installs and blockages across Lagos.", 8, "Lagos",
             "Emergency pipe repair", "Fast response for leaks, burst pipes and blocked drains. Same-day service within Lagos.", 15000, 90),
            ("ngozi", "Ngozi", "Eze", "SparkRight Electrical", "electrical",
             "Certified electrician handling wiring, fault-finding and installations safely.", 6, "Lagos",
             "Home rewiring & fault fixing", "Full diagnostic and repair for tripping breakers, dead sockets and faulty wiring.", 20000, 120),
            ("chidi", "Chidi", "Okoro", "CleanSweep Pro", "cleaning",
             "Deep-cleaning specialist for homes and offices, eco-friendly products only.", 4, "Abuja",
             "Deep home cleaning", "Full deep clean: kitchen, bathrooms, floors and windows. 2-person crew, half-day job.", 12000, 240),
            ("amara", "Amara", "Nwosu", "SwiftMove Logistics", "moving",
             "Runs a small moving crew for apartment and office relocations.", 5, "Lagos",
             "Apartment moving (1-2 bedroom)", "Loading, transport and unloading with padding for furniture. Includes 2 movers and a van.", 35000, 180),
            ("bola", "Bola", "Fashola", "Fresh Coat Painters", "painting",
             "Interior and exterior painting with clean, sharp finishes.", 7, "Ibadan",
             "Interior room painting", "One coat of primer, two coats of paint, per standard-size room. Paint not included.", 18000, 300),
            ("segun", "Segun", "Balogun", "FixIt Appliance Repair", "appliance-repair",
             "Repairs fridges, washing machines, and AC units — mostly same-day.", 5, "Lagos",
             "Fridge & washing machine repair", "Diagnosis plus repair for common faults. Parts billed separately if needed.", 10000, 60),
        ]

        for username, first, last, biz, cat_slug, bio, years, city, s_title, s_desc, s_price, s_dur in providers_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "email": f"{username}@fixitnow.app"},
            )
            if created:
                user.set_password("demopass123")
                user.save()
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    "role": "provider", "city": city, "phone": "+2348000000000",
                    "business_name": biz, "bio": bio, "years_experience": years,
                    "is_approved": True,
                },
            )
            Service.objects.get_or_create(
                provider=user, title=s_title,
                defaults={
                    "category": categories[cat_slug], "description": s_desc,
                    "price": s_price, "duration_minutes": s_dur, "city": city,
                    "is_active": True,
                },
            )

        client, created = User.objects.get_or_create(
            username="funke", defaults={"first_name": "Funke", "last_name": "Adeyemi", "email": "funke@example.com"}
        )
        if created:
            client.set_password("demopass123")
            client.save()
        Profile.objects.get_or_create(
            user=client, defaults={"role": "client", "city": "Lagos", "phone": "+2348011111111"}
        )

        tunde_service = Service.objects.filter(provider__username="tunde").first()
        if tunde_service and not Booking.objects.filter(client=client, service=tunde_service).exists():
            booking = Booking.objects.create(
                client=client, service=tunde_service,
                scheduled_date=datetime.date.today() - datetime.timedelta(days=3),
                scheduled_time=datetime.time(10, 0),
                address="14 Adeola Odeku St, Victoria Island, Lagos",
                notes="Kitchen sink pipe leaking under the cabinet.",
                status="completed",
            )
            Review.objects.get_or_create(
                booking=booking, defaults={"rating": 5, "comment": "Fixed it in under an hour. Very professional."}
            )

        ngozi_service = Service.objects.filter(provider__username="ngozi").first()
        if ngozi_service and not Booking.objects.filter(client=client, service=ngozi_service).exists():
            Booking.objects.create(
                client=client, service=ngozi_service,
                scheduled_date=datetime.date.today() + datetime.timedelta(days=2),
                scheduled_time=datetime.time(14, 0),
                address="14 Adeola Odeku St, Victoria Island, Lagos",
                notes="Living room sockets keep tripping the breaker.",
                status="confirmed",
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Demo logins (password: demopass123):")
        self.stdout.write("  Providers: tunde, ngozi, chidi, amara, bola, segun")
        self.stdout.write("  Client: funke")
