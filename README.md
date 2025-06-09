# Django Project with PostgreSQL

This is a Django project configured to use PostgreSQL.

## Local Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up PostgreSQL:**
    *   Ensure PostgreSQL is installed and running on your system.
    *   Create a new PostgreSQL database. For example, using `psql`:
        ```sql
        CREATE DATABASE your_db_name;
        CREATE USER your_db_user WITH PASSWORD 'your_db_password';
        GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
        ```
        Replace `your_db_name`, `your_db_user`, and `your_db_password` with your desired values.

5.  **Configure Django database settings:**
    *   Open `myproject/settings.py`.
    *   Update the `DATABASES` section with your actual PostgreSQL credentials:
        ```python
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'your_db_name',       # Replace with your DB name
                'USER': 'your_db_user',       # Replace with your DB user
                'PASSWORD': 'your_db_password', # Replace with your DB password
                'HOST': 'localhost',          # Or your DB host
                'PORT': '',                  # Default is 5432
            }
        }
        ```

6.  **Run Django migrations:**
    ```bash
    python manage.py migrate
    ```

7.  **Create a superuser (optional, for accessing the admin panel):**
    ```bash
    python manage.py createsuperuser
    ```

8.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be accessible at `http://127.0.0.1:8000/`.
