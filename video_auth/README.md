# VideoAuth

A Django web application for user authentication with video verification.

## Features
- User registration and login
- Dashboard with video verification status
- Video upload/record (MP4, max 50MB)
- Profile page with embedded video
- Admin controls for verification
- Responsive UI with TailwindCSS

## Setup Instructions

### 1. Create and activate virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```
pip install -r requirements.txt
```


### 3. Make migrations and migrate
```
python manage.py makemigrations
python manage.py migrate
```

### 4. Create superuser
```
python manage.py createsuperuser
```

### 5. Run development server
```
python manage.py runserver
```

Access the app at http://127.0.0.1:8000/

---

## Project Structure
- videoauth_project/: Django project settings
- accounts/: User authentication and profile app
- templates/: HTML templates
- static/: Static files (TailwindCSS)
- media/: Uploaded videos

---

## Requirements
- Python 3.10+
- Django (latest stable)
- TailwindCSS

---

## Notes
- Only logged-in users can access dashboard/profile
- Video uploads: mp4, webm, mov only
- Admin can verify users via Django admin
