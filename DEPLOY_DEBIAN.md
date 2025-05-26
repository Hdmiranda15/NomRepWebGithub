# Instructions to Run the Django, Nginx, Gunicorn Project on Your Debian VM

These instructions will guide you through deploying and running the Django application with Gunicorn and Nginx on your Debian-based Linux virtual machine (VM).

**Project Root:** The "project root" refers to the main directory where you cloned this repository (e.g., `/home/your_user/my_django_project_on_vm/`). In the context of the sandbox environment where this project was developed, the project root was `/app/`. You will need to adjust paths accordingly.

## 1. System Update and Initial Setup

Update your system packages:
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

Install Python, pip, venv, and Git if they are not already installed:
```bash
sudo apt-get install -y python3 python3-pip python3-venv git
```

## 2. Clone the Project

Clone your project repository to your VM (if you haven't already):
```bash
git clone <your_repository_url> project_root
cd project_root
```
Replace `<your_repository_url>` with the actual URL of your Git repository and `project_root` with your desired project directory name.

## 3. Set Up Python Virtual Environment and Install Dependencies

Navigate to your project root directory on the VM:
```bash
cd /path/to/your/project_root # e.g., cd /home/your_user/my_django_project_on_vm
```

Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the Python dependencies:
```bash
pip install -r requirements.txt
```
The `requirements.txt` file should contain:
```
Django==5.2.1
gunicorn==23.0.0
```
(If `pip` points to Python 2, you might need to use `pip3` instead).

## 4. Configure Django Settings

Your Django project is in the `django_project` subdirectory.

**a. Edit `settings.py`:**
Open `django_project/django_project/settings.py` (relative to your project root).
   - **`ALLOWED_HOSTS`**: Add your VM's public IP address or domain name to the `ALLOWED_HOSTS` list. For example: `ALLOWED_HOSTS = ['your_vm_ip_or_domain', 'localhost', '127.0.0.1']`
   - **`DEBUG`**: For production, set `DEBUG = False`. If `DEBUG` is `False`, you *must* correctly configure `ALLOWED_HOSTS`.
   - **`STATIC_ROOT`**: Ensure `STATIC_ROOT` is correctly set. The current configuration in the project is `STATIC_ROOT = os.path.join(BASE_DIR, '..', 'staticfiles')`. This means static files will be collected into a directory named `staticfiles` in your project root (alongside `django_project/`, `gunicorn/`, etc.). This path should be fine.

**b. Collect Static Files:**
From the `django_project` directory (e.g., `/path/to/your/project_root/django_project/`), run:
```bash
python manage.py collectstatic --noinput
```
This will copy all static files (CSS, JS, images from your apps and Django admin) into the `staticfiles` directory at your project root.

## 5. Configure and Run Gunicorn

Gunicorn will serve your Django application. The configuration for Gunicorn is in `gunicorn/gunicorn_config.py` (relative to your project root).

**a. Review `gunicorn_config.py`:**
The provided configuration is:
```python
import multiprocessing

# Gunicorn will bind to 0.0.0.0:8000, accessible from any network interface.
# Nginx will proxy requests to this.
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1

# Important: chdir should be the directory containing your Django project's manage.py
# In the cloned structure, this is 'django_project' relative to the gunicorn_config.py parent.
# If gunicorn_config.py is in /path/to/your/project_root/gunicorn/,
# and manage.py is in /path/to/your/project_root/django_project/, this is correct.
chdir = "django_project"

# Path to the WSGI application object
module = "django_project.wsgi:application"

# Optional: Logging (uncomment and adjust paths if needed)
# accesslog = "/var/log/gunicorn/access.log"
# errorlog = "/var/log/gunicorn/error.log"
# loglevel = "info" # "debug", "info", "warning", "error", "critical"
```
Ensure `chdir` correctly points to your Django project directory (where `manage.py` is located) relative to where you run Gunicorn, or use an absolute path. The current relative path `django_project` assumes Gunicorn is run from the project root.

**b. Test Gunicorn Manually (Optional but Recommended):**
Navigate to your project root: `cd /path/to/your/project_root/`
Then run Gunicorn directly:
```bash
venv/bin/gunicorn -c gunicorn/gunicorn_config.py
```
Or, if you want to specify the module directly (ensure `chdir` in the config is commented out or not conflicting):
```bash
venv/bin/gunicorn --chdir django_project django_project.wsgi:application -b 0.0.0.0:8000 --workers 3
```
Open your browser and go to `http://YOUR_VM_IP_OR_DOMAIN:8000`. You should see your Django app. Press `Ctrl+C` to stop Gunicorn. If this works, Gunicorn is configured correctly.

**c. Running Gunicorn as a Service (Systemd - Recommended for Production):**
Create a systemd service file for Gunicorn:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```
Paste the following content, carefully adjusting paths:
```ini
[Unit]
Description=gunicorn daemon for Django project
After=network.target

[Service]
User=your_user                             # Replace with your username
Group=www-data                             # Or your_user if not using www-data for Nginx
WorkingDirectory=/path/to/your/project_root # Replace with your project root
ExecStart=/path/to/your/project_root/venv/bin/gunicorn -c /path/to/your/project_root/gunicorn/gunicorn_config.py

# Optional: Environment variables (e.g., for Django settings)
# Environment="DJANGO_SETTINGS_MODULE=django_project.settings"
# Environment="PYTHONUNBUFFERED=1"

Restart=always
StandardOutput=append:/var/log/gunicorn/gunicorn_stdout.log # Ensure this dir exists and has perms
StandardError=append:/var/log/gunicorn/gunicorn_stderr.log  # Ensure this dir exists and has perms
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```
   - Replace `your_user` with your actual Linux username on the VM.
   - Replace `/path/to/your/project_root` with the absolute path to your project's root directory.
   - Ensure the log directory (e.g., `/var/log/gunicorn/`) exists and has appropriate permissions for `your_user` to write to it:
     ```bash
     sudo mkdir -p /var/log/gunicorn
     sudo chown your_user:your_user /var/log/gunicorn # Or your_user:www-data if Nginx needs access
     ```

Start and enable the Gunicorn service:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```
Check its status:
```bash
sudo systemctl status gunicorn
```
Check logs if there are issues:
```bash
sudo journalctl -u gunicorn
cat /var/log/gunicorn/gunicorn_stderr.log
```

## 6. Install and Configure Nginx

Nginx will act as a reverse proxy, serving static files directly and passing dynamic requests to Gunicorn.

**a. Install Nginx:**
```bash
sudo apt-get install -y nginx
```

**b. Create Nginx Server Block Configuration:**
The project includes a template `nginx/django_app.conf`. You should copy this to Nginx's configuration directory.

From your project root (`/path/to/your/project_root/`):
```bash
sudo cp nginx/django_app.conf /etc/nginx/sites-available/my_django_app.conf
```
Now, edit the copied Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/my_django_app.conf
```
   - **`server_name YOUR_VM_IP_OR_DOMAIN;`**: Replace `YOUR_VM_IP_OR_DOMAIN` with your VM's public IP address or domain name.
   - **`set $project_root /path/to/your/project_root;`**: Replace `/path/to/your/project_root` with the actual absolute path to your project's root directory on the VM (e.g., `/home/your_user/my_django_project_on_vm`). This variable is used for the `alias` directive for static files.

The relevant parts of `django_app.conf` to modify:
```nginx
# /etc/nginx/sites-available/my_django_app.conf

server {
    listen 80;
    server_name YOUR_VM_IP_OR_DOMAIN; # <-- EDIT THIS

    set $project_root /path/to/your/project_root; # <-- EDIT THIS

    access_log /var/log/nginx/django_app_access.log;
    error_log /var/log/nginx/django_app_error.log;

    location /static/ {
        alias $project_root/staticfiles/; # Static files collected by Django
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000; # Gunicorn's address
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

**c. Enable the Site and Test Nginx Configuration:**
Create a symbolic link from `sites-available` to `sites-enabled`:
```bash
sudo ln -sf /etc/nginx/sites-available/my_django_app.conf /etc/nginx/sites-enabled/my_django_app.conf
```
Remove the default Nginx site if it's enabled (to avoid conflicts):
```bash
sudo rm -f /etc/nginx/sites-enabled/default
```
Test your Nginx configuration:
```bash
sudo nginx -t
```
If the test is successful, restart Nginx:
```bash
sudo systemctl restart nginx
```
If Nginx fails to start or the test fails, check the Nginx error logs:
```bash
sudo systemctl status nginx
sudo journalctl -u nginx
cat /var/log/nginx/error.log
cat /var/log/nginx/django_app_error.log
```

## 7. Access Your Application

Open your web browser and navigate to `http://YOUR_VM_IP_OR_DOMAIN`. You should see your Django application.
   - Test a static file directly: `http://YOUR_VM_IP_OR_DOMAIN/static/myapp/css/style.css`

## 8. Firewall Configuration (If Applicable)

If you have a firewall (like `ufw`) enabled on your VM, ensure it allows HTTP (port 80) and HTTPS (port 443, if you set it up) traffic:
```bash
sudo ufw allow 'Nginx Full' # Allows both HTTP and HTTPS
# OR
sudo ufw allow 'Nginx HTTP' # Allows only HTTP
sudo ufw status
```

## Troubleshooting Tips

*   **Permissions:** Ensure that the user running Gunicorn (e.g., `your_user`) has read/write access to necessary project directories and log files. Nginx's worker processes (often user `www-data`) need read access to static files and write access to its log files.
*   **Paths:** Double-check all absolute paths in your Gunicorn service file and Nginx configuration.
*   **`collectstatic`:** If static files are not appearing, ensure `STATIC_ROOT` is correct and `collectstatic` was run successfully. Verify the files exist in your `STATIC_ROOT` directory.
*   **Gunicorn Logs:** `sudo journalctl -u gunicorn` or `/var/log/gunicorn/gunicorn_stderr.log` (if configured).
*   **Nginx Logs:** `/var/log/nginx/error.log` and `/var/log/nginx/django_app_error.log`.
*   **Django `DEBUG = False`:** If `DEBUG` is `False` and you see a 500 error, Django might not be able to find your static files or there's another issue it's hiding. Check Django logs (if configured) or temporarily set `DEBUG = True` (with `ALLOWED_HOSTS` set) for more detailed error messages *during development only*.
*   **SELinux/AppArmor:** If your Debian system has SELinux or AppArmor enabled with strict policies, they might interfere. You may need to adjust their policies if standard permissions seem correct but access is still denied. (This is less common on default Debian installs compared to RHEL-based systems for SELinux).
*   **`ALLOWED_HOSTS`:** If you get "DisallowedHost" errors, make sure your VM's IP or domain is correctly listed in `settings.py`.
```
