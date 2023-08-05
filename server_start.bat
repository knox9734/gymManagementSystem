@echo off
REM Replace "C:\path\to\your\virtualenv" with the path to your virtual environment
call C:\face_auth\face_auth.venv\Scripts\activate
cd /d C:\face_auth\staff_auth_app
python manage.py runserver
