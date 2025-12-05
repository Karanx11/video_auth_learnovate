# Video-Auth Upload Platform

A simple Django-based web application that lets authenticated users upload and manage videos via a dashboard UI.

## 🚀 What is this?

This project allows users to sign up / log in, and then upload video files seamlessly.  
The uploaded videos are stored under `media/`, while the UI and upload logic are handled via Django apps with authentication and video-upload support.  

## 🔧 Features

- ✅ User authentication (signup / login / logout)  
- ✅ Secure video upload and management  
- ✅ Dashboard for viewing, uploading and managing videos  
- ✅ Media storage (uploaded video files)  
- ✅ Modular Django project structure (apps, static, templates)  

## 🛠️ Tech Stack

- Python 3.x  
- Django (web framework)  
- SQLite (default DB) — or any other DB if you configure settings  
- HTML / CSS / Bootstrap (or frontend templating) for UI  
- Django static & media settings for video upload & serve  

## 📁 Project Structure (simplified)

VIDEO_AUTH/
  ├── video_auth/ ← Django project folder
  │ ├── manage.py ← Entry point for Django commands
  │ ├── ... ← settings, urls, wsgi, etc.
  ├── accounts/ ← Django app: authentication (sign-up/login)
  ├── media/ ← Uploaded video files stored here
  ├── static/ ← Static files (css, js, images)
  ├── templates/ ← HTML templates for frontend & dashboard
  ├── venv/ ← Virtual environment (not to be committed)
  └── README.md ← This file



## 🧰 Setup & Run Locally

# Clone the repository
git clone https://github.com/Karanx11/video_auth_learnovate.git

cd video_auth_learnovate/video_auth       # or the correct path containing manage.py

# (Recommended) create & activate a virtual environment
python -m venv venv
# Windows:
venv\\Scripts\\activate
# macOS / Linux:
# source venv/bin/activate

# Install dependencies
pip install django   # or pip install -r requirements.txt if you have one

# Run database migrations
python manage.py migrate

# Run the development server
python manage.py runserver

# Open your browser at:
http://127.0.0.1:8000/

✅ Usage
Register a new user or log in with existing credentials

Navigate to /dashboard/ to access the video-upload dashboard

Upload videos via the upload form

Uploaded videos will be saved in the media/ folder and listed in the dashboard

