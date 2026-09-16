from django.core.management.base import BaseCommand

from core.models import Category


class Command(BaseCommand):
    help = "Seed the full FixItNow service category list"

    def handle(self, *args, **options):
        categories = [
            ("Plumbing", "plumbing"),
            ("Electrical", "electrical"),
            ("Cleaning", "cleaning"),
            ("Moving", "moving"),
            ("Painting", "painting"),
            ("Appliance Repair", "appliance-repair"),
            ("Gardening", "gardening"),
            ("Carpentry", "carpentry"),
            ("HVAC/AC Repair & Installation", "hvac-ac-repair-installation"),
            ("Roofing", "roofing"),
            ("Masonry/Bricklaying", "masonry-bricklaying"),
            ("Tiling", "tiling"),
            ("Welding & Metalwork", "welding-metalwork"),
            ("Glass & Window Repair", "glass-window-repair"),
            ("Locksmith", "locksmith"),
            ("Generator Repair & Servicing", "generator-repair-servicing"),
            ("Solar Panel Installation & Repair", "solar-panel-installation-repair"),
            ("Borehole/Water System Services", "borehole-water-system-services"),
            ("Fumigation & Pest Control", "fumigation-pest-control"),
            ("Deep Cleaning", "deep-cleaning"),
            ("Laundry & Dry Cleaning", "laundry-dry-cleaning"),
            ("Carpet & Upholstery Cleaning", "carpet-upholstery-cleaning"),
            ("Post-Construction Cleaning", "post-construction-cleaning"),
            ("Window Cleaning", "window-cleaning"),
            ("Septic Tank/Waste Services", "septic-tank-waste-services"),
            ("POP/Ceiling Design", "pop-ceiling-design"),
            ("Fencing & Gate Installation", "fencing-gate-installation"),
            ("Paving & Concrete Work", "paving-concrete-work"),
            ("Swimming Pool Maintenance", "swimming-pool-maintenance"),
            ("Furniture Assembly", "furniture-assembly"),
            ("Delivery/Errand Services", "delivery-errand-services"),
            ("Storage Solutions", "storage-solutions"),
            ("Hairdressing/Barbing", "hairdressing-barbing"),
            ("Makeup Artistry", "makeup-artistry"),
            ("Nail Technician", "nail-technician"),
            ("Spa/Massage Therapy", "spa-massage-therapy"),
            ("Catering", "catering"),
            ("Event Decoration", "event-decoration"),
            ("DJ/MC Services", "dj-mc-services"),
            ("Photography & Videography", "photography-videography"),
            ("Tent & Canopy Rental", "tent-canopy-rental"),
            ("Computer/Phone Repair", "computer-phone-repair"),
            ("CCTV Installation", "cctv-installation"),
            ("Networking/Wi-Fi Setup", "networking-wi-fi-setup"),
            ("Home Automation/Smart Home Setup", "home-automation-smart-home-setup"),
            ("Tutoring/Home Lessons", "tutoring-home-lessons"),
            ("Nanny/Babysitting Services", "nanny-babysitting-services"),
            ("House Help/Domestic Staff", "house-help-domestic-staff"),
            ("Elderly Care/Home Care Assistance", "elderly-care-home-care-assistance"),
            ("Car Wash (mobile)", "car-wash-mobile"),
            ("Auto Mechanic (mobile)", "auto-mechanic-mobile"),
            ("Car AC Repair", "car-ac-repair"),
            ("Tailoring/Fashion Design", "tailoring-fashion-design"),
            ("Upholstery/Furniture Repair", "upholstery-furniture-repair"),
            ("Key Cutting", "key-cutting"),
            ("Interior Design Consultation", "interior-design-consultation"),
        ]

        created = 0
        skipped = 0
        for name, slug in categories:
            _, was_created = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Categories: {created} created, {skipped} already existed."
        ))
