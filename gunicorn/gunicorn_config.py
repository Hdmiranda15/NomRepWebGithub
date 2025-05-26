import multiprocessing

bind = "0.0.0.0:8000"  # Bind to all network interfaces on port 8000
workers = multiprocessing.cpu_count() * 2 + 1
# accesslog = "-"  # Log to stdout
# errorlog = "-"   # Log to stderr
# loglevel = "info"
chdir = "django_project"  # Change directory to the Django project folder
module = "django_project.wsgi:application" # Path to the WSGI application
