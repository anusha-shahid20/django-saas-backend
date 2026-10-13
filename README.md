# Django SaaS Backend

A multi-tenant SaaS backend built with Django and Django REST Framework. This project demonstrates production-grade backend patterns including JWT authentication, role-based access control, multi-tenancy, data isolation, soft delete, audit logging, and background tasks.

## Features

- **JWT Authentication** — Secure token-based authentication with access and refresh tokens
- **Multi-Tenancy** — Complete data isolation between companies (tenants)
- **Role-Based Access Control** — Admin, Manager, and Employee roles
- **Projects & Tasks CRUD** — Full REST APIs for managing projects and tasks
- **Soft Delete** — Deleted records are marked, not removed from database
- **Audit Logging** — Automatic tracking of who did what and when
- **Rate Limiting** — Throttling on login endpoint to prevent brute-force attacks
- **Background Tasks** — Celery setup for asynchronous email sending

## Tech Stack

- **Python 3.14**
- **Django 6.1**
- **Django REST Framework**
- **SimpleJWT** — JWT authentication
- **Celery** — Background tasks
- **SQLite** — Development database (PostgreSQL recommended for production)

## Project Structure

```
django-saas-backend/
├── config/                  # Django project settings
│   ├── settings.py          # Project settings
│   ├── urls.py              # Root URL configuration
│   └── celery.py            # Celery configuration
├── tasks/                   # Main app
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API views
│   ├── urls.py              # App URLs
│   ├── admin.py             # Admin registration
│   ├── signals.py           # Signal handlers for audit logging
│   ├── tasks.py             # Celery background tasks
│   ├── auth_views.py        # Custom JWT login with throttling
│   └── tests.py             # Unit tests
├── venv/                    # Virtual environment (not in repo)
├── .gitignore
├── manage.py
├── postman_collection.json  # Postman API collection
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/anusha-shahid20/django-saas-backend.git
cd django-saas-backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt celery
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Server will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/token/` | Login — get access & refresh tokens | No |
| POST | `/api/token/refresh/` | Refresh access token | No |

### Projects

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks/api/projects/` | List all projects (own company only) | Yes |
| POST | `/tasks/api/projects/` | Create a new project | Yes |
| GET | `/tasks/api/projects/<id>/` | Get project details | Yes |
| PUT | `/tasks/api/projects/<id>/` | Update project | Yes |
| DELETE | `/tasks/api/projects/<id>/` | Soft delete project | Yes |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks/api/tasks/` | List all tasks (own company only) | Yes |
| POST | `/tasks/api/tasks/` | Create a new task | Yes |
| GET | `/tasks/api/tasks/<id>/` | Get task details | Yes |
| PUT | `/tasks/api/tasks/<id>/` | Update task | Yes |
| PATCH | `/tasks/api/tasks/<id>/` | Partially update task | Yes |
| DELETE | `/tasks/api/tasks/<id>/` | Delete task | Yes |
| PATCH | `/tasks/api/tasks/<id>/status/` | Update only the status | Yes |

## Authentication Flow

1. **Signup:** Create a user via Django admin or shell.
2. **Login:** Send POST request to `/api/token/` with username and password.
3. **Receive tokens:** Server returns `access` and `refresh` tokens.
4. **Use access token:** Include in every request header:
   ```
   Authorization: Bearer <access_token>
   ```
5. **Refresh when expired:** Send refresh token to `/api/token/refresh/` to get a new access token.

### Example Login Request

```http
POST /api/token/
Content-Type: application/json

{
    "username": "admin",
    "password": "your_password"
}
```

### Example Response

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Example Authenticated Request

```http
GET /tasks/api/projects/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Multi-Tenancy & Data Isolation

This backend follows a **shared database, shared schema** multi-tenancy model:

- Every user belongs to a `Company` via `UserProfile`.
- Every `Project` belongs to a `Company`.
- Every `Task` belongs to a `Project` (and thus to a `Company`).
- **Every query is filtered by the user's company** — no cross-tenant data leaks.
- `Company A` cannot see, modify, or delete `Company B`'s data.

## Security Features

- **JWT Authentication** — No session cookies, stateless auth.
- **Permission Classes** — `IsAuthenticated` on all sensitive endpoints.
- **Data Isolation** — Every query filters by `company`.
- **Rate Limiting** — Login endpoint throttled to 5 attempts per minute.
- **Soft Delete** — Deleted records remain in database for recovery.
- **Audit Logging** — Every project change is logged.

## Running Tests

```bash
python manage.py test
```

The test suite includes tenant isolation tests to verify that users from one company cannot access another company's data.

## Admin Panel

Access the Django admin at `http://127.0.0.1:8000/admin/` with your superuser credentials.

## Postman Collection

Import `postman_collection.json` into Postman to test all API endpoints. Update the `access_token` variable after logging in.

## Future Improvements

- [ ] Add Swagger/OpenAPI documentation
- [ ] Add pagination for large lists
- [ ] Add filtering and search
- [ ] Set up Redis for Celery in production
- [ ] Add Docker support
- [ ] Deploy to production (Railway, Render, etc.)
- [ ] Add email verification on signup

## Author

**Anusha Shahid**
GitHub: [@anusha-shahid20](https://github.com/anusha-shahid20)

## License

This project is for educational purposes as part of a backend engineering training program.