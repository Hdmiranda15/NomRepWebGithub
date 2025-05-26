# Django, Nginx, Gunicorn Project

This project sets up a basic Django application served by Gunicorn and fronted by Nginx as a reverse proxy.
It includes a simple HTML page with CSS and JavaScript.

## Project Structure Overview

*   `django_project/`: Contains the Django project itself.
    *   `myapp/`: A sample Django application within the project.
    *   `django_project/`: Contains project-level settings, URLs, etc.
    *   `manage.py`: Django's command-line utility.
*   `gunicorn/`: Contains Gunicorn configuration (`gunicorn_config.py`).
*   `nginx/`: Contains Nginx configuration templates.
    *   `nginx.conf`: Original full HTTP block for Nginx (can be used for reference or specific setups).
    *   `django_app.conf`: A server block template suitable for inclusion in standard Nginx `sites-available` configurations on Debian/Ubuntu.
*   `staticfiles/`: Directory where Django's `collectstatic` command gathers all static assets. This is served by Nginx.
*   `requirements.txt`: Python dependencies (Django, Gunicorn).
*   `venv/`: (Recommended) Python virtual environment directory (not included in repo).

## Deployment

For detailed instructions on how to deploy and run this project on a Debian Linux VM, please see:
[**DEPLOY_DEBIAN.md**](./DEPLOY_DEBIAN.md)

---
# NomRepWebGithub
