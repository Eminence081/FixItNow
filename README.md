# FixItNow

A local trades marketplace — plumbers, electricians, cleaners, movers.
Clients browse services, book a slot, and pay on completion. Providers
list services, confirm/decline bookings, and get reviewed.

## Local setup

```bash
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # optional: adds demo providers/services/bookings
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## Demo accounts (after running seed_demo)

Password for all: `demopass123`

- Providers: `tunde` (plumbing), `ngozi` (electrical), `chidi` (cleaning),
  `amara` (moving), `bola` (painting), `segun` (appliance repair)
- Client: `funke`

## Structure

- `core/models.py` — Profile (client/provider), Category, Service, Booking, Review
- `core/views.py` — browse/search, service detail, booking flow, provider dashboard, delete actions
- `core/forms.py` — registration, service listing, booking, review forms
- `templates/core/` — Bootstrap 5 templates
- `static/css/style.css` — custom design system (navy/amber "job ticket" theme)
- `static/js/main.js` — interactive star-rating picker, live form validation, booking-date guard

## CRUD coverage

- **Create**: register, list a service, make a booking, leave a review
- **Read**: browse/search services, service detail, provider list, dashboards
- **Update**: edit service, edit profile, booking status transitions
- **Delete**: delete a service listing, delete a finished/cancelled booking record, delete a review — each behind a confirm-delete page

## Deploying

### Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/fixitnow.git
git push -u origin main
```

The `.gitignore` already excludes `venv/`, `db.sqlite3`, `media/`, `staticfiles/`,
and `.env` — none of those should be committed.

### Deploy to AWS Elastic Beanstalk

This project is already configured for EB:
- `Procfile` tells EB to run it with gunicorn
- `.ebextensions/django.config` runs migrations and `collectstatic` on every deploy
- `requirements.txt` lists all dependencies (Django, gunicorn, whitenoise, Pillow)
- `settings.py` reads `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` from environment
  variables, so nothing sensitive is hardcoded for production

Steps:

```bash
pip install awsebcli
eb init -p python-3.13 fixitnow
eb create fixitnow-env
```

Then, in the EB console (or via `eb setenv`), set these environment properties
**before** or right after the first deploy:

```
DJANGO_SECRET_KEY=<a long random string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<your-env>.elasticbeanstalk.com,.elasticbeanstalk.com
```

Example with the CLI:

```bash
eb setenv DJANGO_SECRET_KEY="paste-a-random-50-char-string-here" DJANGO_DEBUG=False DJANGO_ALLOWED_HOSTS=".elasticbeanstalk.com"
```

Then deploy any future changes with:

```bash
eb deploy
```

**Note on the database:** by default this uses SQLite, which does not
persist reliably on Elastic Beanstalk (the instance can be replaced,
wiping local files). That's fine for a demo/portfolio deployment. For a
real production app, provision an RDS PostgreSQL instance and update
`DATABASES` in `settings.py` accordingly.

**When you're done demoing:** run `eb terminate fixitnow-env` to avoid
any ongoing AWS charges — don't just leave the environment running.

## Next steps you could add

- Real payments (Paystack/Flutterwave) instead of "pay on completion"
- Provider approval workflow (currently auto-approved)
- In-app messaging between client and provider
- Availability calendar instead of free-text date/time
- Swap SQLite for PostgreSQL/RDS for a persistent production database
