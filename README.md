# Blog API

A production-oriented RESTful Blog API built with **FastAPI**. The API provides user authentication, blog post management, social interactions, media uploads, role-based access control, and administrative management.

The project is designed with a modular architecture and uses asynchronous programming where appropriate to provide a scalable and maintainable backend.

## Tech Stack

- **Python**
- **FastAPI** — Web framework
- **MySQL** — Relational database
- **SQLAlchemy** — ORM
- **Alembic** — Database migrations
- **Redis** — Caching, token management, OTP storage, and token invalidation
- **Cloudinary** — Media storage and management
- **Celery** — Background task processing
- **JWT** — Authentication and authorization
- **Pydantic** — Data validation and serialization
- **Argon2** — Password hashing

---

# Features

## Authentication & Security

The API provides a complete authentication system including:

- User registration
- Email verification using verification tokens
- Login
- Logout
- Forgot password
- OTP-based password reset
- Change password
- Access and refresh tokens
- Refresh token rotation
- JWT-based authentication
- Token invalidation using Redis
- Password hashing with Argon2
- Role-based access control

### Authentication Flow

```text
Register
   ↓
Email Verification
   ↓
Login
   ↓
Access Token + Refresh Token
   ↓
Access Protected Resources
   ↓
Refresh Token
   ↓
New Access Token + New Refresh Token
```

### Email Verification
```text 
When a user registers, the API generates an email verification token.

User Registration
       ↓
Verification Token Generated
       ↓
Email Sent
       ↓
User Clicks Verification Link
       ↓
Token Validated
       ↓
Account Activated

Redis is used to support token invalidation and expiration handling.
```

### Password Management
```text
The authentication system supports:

Forgot Password
Enter Email
    ↓
OTP Generated
    ↓
OTP Stored in Redis
    ↓
OTP Sent to User
    ↓
OTP Verification
    ↓
Password Reset Token
    ↓
New Password

Users can also change their password while authenticated.
```

### Refresh Token Rotation
```text
The API uses access and refresh tokens.

When a refresh token is used:

Old Refresh Token
       ↓
Validated
       ↓
Invalidated
       ↓
New Access Token
       +
New Refresh Token

This helps reduce the security risks associated with long-lived refresh tokens.
```

### Database
```text
The application uses MySQL as its relational database.

SQLAlchemy is used as the ORM for database interactions.

Database schema changes are managed using Alembic.


#Create a migration
alembic revision --autogenerate -m "your migration message"

#Run migrations
alembic upgrade head

 #Redis

Redis is used for several application-level operations, including:

Refresh token storage
Token blacklisting/invalidation
OTP storage
Temporary authentication data
Caching

This allows short-lived authentication data to be handled efficiently without unnecessarily storing everything in MySQL.
```

### Cloudinary
```text
The API integrates with Cloudinary for media management.

Instead of storing uploaded media directly on the application server, media files are uploaded to Cloudinary and their references are stored by the application.

This makes media storage more suitable for deployment and production environments.
```

## User Roles

The API supports different user roles and permissions.

### Reader

```text
View blog posts
Like posts
Comment on posts
Bookmark posts
Manage their account
```

### Authors 
```text
Create posts
Update their posts
Delete their posts
Attach media to posts
Manage content associated with their posts
Perform reader-level interactions
```
### Admin
```text
Administrators have elevated privileges and can:

Manage users
Manage posts
Manage categories and tags
Manage comments
Manage application resources
Access administrative functionality
```

## Blog Posts
```test
Users with the appropriate permissions can create and manage blog posts.

Posts support:

Title
Content
Author
Categories
Tags
Optional media
Likes
Comments
Bookmarks
```
### Supported Media
    #Media can be uploaded and stored using Cloudinary.

#### image
- .jpeg
- .png
- .gif
- .webp
#### media
- pdf
- docx

## Project Structure

```text
blog_system/
│
├── admin/
│   ├── __init__.py
│   └── admin.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── celery_tasks/
│   ├── __init__.py
│   ├── celery_instance.py
│   └── celery_tasks.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── redis_setup.py
│   └── security.py
│
├── middleware/
│   ├── __init__.py
│   ├── logging.py
│   └── rate_limiter.py
│
├── models/
│   ├── __init__.py
│   ├── auditlog.py
│   ├── base.py
│   ├── bookmark.py
│   ├── category.py
│   ├── comment.py
│   ├── likes.py
│   ├── media.py
│   ├── notification.py
│   ├── post_tag.py
│   └── user.py
│
├── repositories/
│   ├── __init__.py
│   ├── audit_repository.py
│   ├── auth_repository.py
│   ├── base.py
│   ├── bookmark_repository.py
│   ├── category_repository.py
│   ├── comment_repository.py
│   ├── like_repository.py
│   ├── media_repository.py
│   ├── notification_repository.py
│   ├── post_repository.py
│   ├── tag_repository.py
│   └── user_repository.py
│
├── routes/
│   ├── __init__.py
│   ├── audit.py
│   ├── auth.py
│   ├── bookmark.py
│   ├── categories.py
│   ├── comments.py
│   ├── likes.py
│   ├── media.py
│   ├── notification.py
│   ├── post.py
│   ├── tags.py
│   └── user.py
│
├── schemas/
│   ├── __init__.py
│   ├── auditlog.py
│   ├── base.py
│   ├── bookmark.py
│   ├── category.py
│   ├── comment.py
│   ├── likes.py
│   ├── media.py
│   ├── notification.py
│   ├── post.py
│   ├── tags.py
│   └── user.py
│
├── service/
│   ├── __init__.py
│   ├── audit.py
│   ├── auth.py
│   ├── bookmark.py
│   ├── category.py
│   ├── comment.py
│   ├── like.py
│   ├── media.py
│   ├── notification.py
│   ├── post.py
│   ├── tags.py
│   └── user.py
│
├── utility/
│   ├── __init__.py
│   ├── cloud.py
│   ├── dependency.py
│   ├── email.py
│   └── field_utility.py
│
├── alembic.ini
├── main.py
├── requirements.txt
├── README.md
└── .env.example
```

---

# Architecture

The project follows a layered architecture that separates responsibilities between different parts of the application.

                Client
                  │
                  ▼
              FastAPI
                  │
                  ▼
               Routes
                  │
                  ▼
              Services
                  │
                  ▼
            Repositories
                  │
                  ▼
              SQLAlchemy
                  │
                  ▼
                MySQL



# Setup & run
```bash
1. Clone the repository
git clone <repo_url>

cd in directory

2. Create a virtual environment
python -m venv .venv

#Activate it:
Linux/macOS
source .venv/bin/activate
Windows
.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt
```
```text
For environment Variables

Create a .env file in the project root.

NOTE: Never commit your actual .env file or secrets to GitHub.

Use .env.example to document the required environment variables.

For Database 

Create your MySQL database, then configure the database connection in your .env file.
```

## Run the migrations:
```bash
# if you wish to begin from start

- alembic init alembic
- alembic revision --autogenerate -m "your commit message"
- alembic upgrade head

Start the FastAPI development server:

uvicorn main:app --reload

The API will be available at:

http://127.0.0.1:8000

FastAPI automatically provides interactive API documentation.

Swagger UI
http://127.0.0.1:8000/api/v1/docs
ReDoc
http://127.0.0.1:8000/api/v1/docs/redoc

```

# Future Improvements
```text
Possible future improvements include:

 Advanced post filtering
 WebSocket notifications
 Docker deployment
 CI/CD pipeline
 Improved monitoring and observability
```
---

# Author

**Joshua Oguejiofor**

Backend Developer specializing in Python and FastAPI.


# License
This project is intended for learning, development, and demonstration purposes.

