# acws-helpdesk

Django Helpdesk scaffold.

Setup (Windows):
1. Create virtualenv and activate:
   python -m venv .venv
   .venv\Scripts\activate

2. Install:
   pip install -r requirements.txt

3. Copy .env.example -> .env and set `DATABASE_URL` and `DJANGO_SECRET_KEY`.

4. Run migrations and create superuser:
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser

5. Run server:
   python manage.py runserver
