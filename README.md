# Wowdash Django Project

A full-featured Django web application with REST API, user authentication, admin dashboard, and more. This guide will help you set up, configure, and run the project from scratch.

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Database Migration](#database-migration)
- [Running the Development Server](#running-the-development-server)
- [Static Files & Tailwind CSS](#static-files--tailwind-css)
- [Creating a Superuser](#creating-a-superuser)
- [Common Issues & Troubleshooting](#common-issues--troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features
- Django 5.x, REST Framework, Allauth
- Modular app structure (users, blog, FAQ, team, settings, etc.)
- Social authentication
- Environment-based config
- Admin dashboard
- Tailwind CSS for frontend
- SQLite (default) or PostgreSQL support

---

## Requirements
- Python 3.9+
- Node.js & npm (for Tailwind CSS)
- pip

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Wowdash
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies (for Tailwind):**
   ```bash
   npm install
   ```

---

## Environment Configuration

1. **Create your `.env` file:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and set the following:
     - `SECRET_KEY` (Django secret key)
     - `ALLOWED_HOSTS` (comma-separated list, e.g. `127.0.0.1,localhost`)
     - `DEBUG` (`True` or `False`)

2. **Environment Variables Used:**
   - `DJANGO_SECRET_KEY` (maps to `SECRET_KEY`)
   - `DJANGO_ALLOWED_HOSTS` (maps to `ALLOWED_HOSTS`)
   - `DEBUG`

---

## Database Migration

1. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

---

## Running the Development Server

1. **Start Django server:**
   ```bash
   python manage.py runserver
   ```
   - The site will be available at `http://127.0.0.1:8000/`

---

## Static Files & Tailwind CSS

1. **Compile Tailwind CSS:**
   ```bash
   npx tailwindcss -i ./input.css -o ./output.css --watch
   ```
   *(Adjust paths as needed for your setup)*

2. **Collect static files (for production):**
   ```bash
   python manage.py collectstatic
   ```

---

## Creating a Superuser

1. **Create an admin user:**
   ```bash
   python manage.py createsuperuser
   ```
   - Visit `/admin/` to access the Django admin panel.

---

## Common Issues & Troubleshooting

- **Missing dependencies:** Ensure you have run both `pip install -r requirements.txt` and `npm install`.
- **Environment variables not loaded:** Double-check your `.env` file and variable names.
- **Static files not updating:** Run Tailwind build and `collectstatic` as needed.
- **Database errors:** Make sure migrations are applied and DB credentials are correct.
- **Port already in use:** Change the port with `python manage.py runserver 8001`.

---

## Project Structure

```
Wowdash/
├── Wowdash/           # Django project settings, URLs
├── wowdash_app/       # Main Django app (models, views, templates)
├── aiwave/            # Additional app (static, templates, views)
├── requirements.txt   # Python dependencies
├── package.json       # Node.js dependencies (Tailwind)
├── manage.py          # Django CLI entry point
├── .env.example       # Example environment config
├── README.md          # This file
└── ...
```

---

## License
Specify your license here (MIT, Apache 2.0, etc.)

---

## Additional Notes
- For production, configure a real database and set `DEBUG=False`.
- Set proper `ALLOWED_HOSTS` and `SECRET_KEY` in production.
- Review and update `.env` and settings as needed for your deployment.

---

Happy coding!