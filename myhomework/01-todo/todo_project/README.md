This folder contains a minimal Django project and "todos" app for a simple TODO application.

Run instructions:
1. Create and activate a venv named `uv`:
   python3 -m venv uv
   source uv/bin/activate
2. Install dependencies:
   python -m pip install --upgrade pip
   pip install django
3. Apply migrations:
   python manage.py migrate
4. Create a superuser (optional, for admin):
   python manage.py createsuperuser
5. Run the dev server:
   python manage.py runserver

Access the site at http://127.0.0.1:8000/ and admin at /admin/.
