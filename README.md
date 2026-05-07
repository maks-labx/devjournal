# DevJournal

DevJournal is a Django-based blog application with user profiles, post management, categories, tags, comments, ratings, RSS feed, and basic access control.

The project was built as a portfolio-ready Django application with PostgreSQL, Docker, environment-based settings, and automated tests.

## Features

- User registration, login, and logout
- User profiles with avatars and bio
- Create, update, and delete posts
- Draft and published post statuses
- "My posts" dashboard for authors
- Category filtering
- Tag filtering
- Nested comments
- Like / dislike rating system
- RSS feed
- Custom 403, 404, and 500 error pages
- PostgreSQL database
- Docker Compose setup
- Basic automated tests

## Tech Stack

- Python
- Django 5
- PostgreSQL
- Docker / Docker Compose
- Bootstrap 5
- django-mptt
- django-taggit
- django-ckeditor-5
- django-recaptcha
- django-debug-toolbar

## Project Structure

```text
.
├── apps/
│   ├── accounts/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── blog/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── feeds.py
│   │   └── tests.py
│   └── services/
│       ├── mixins.py
│       └── utils.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── accounts/
│   ├── blog/
│   ├── errors/
│   └── includes/
├── media/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── README.md

## Environment Variables

Create a `.env` file in the project root based on `.env.example`.

Example:

```env
SECRET_KEY=change_me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=devjournal
POSTGRES_USER=devjournal_user
POSTGRES_PASSWORD=change_me
POSTGRES_HOST=db
POSTGRES_PORT=5432

RECAPTCHA_PUBLIC_KEY=change_me
RECAPTCHA_PRIVATE_KEY=change_me
```

Do not commit the real `.env` file to Git.

## How to Run Locally

Build and start the containers:

```bash
docker compose up --build
```

Apply migrations:

```bash
docker compose exec web python manage.py migrate
```

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Collect static files if needed:

```bash
docker compose exec web python manage.py collectstatic
```

Open the project in the browser:

```text
http://127.0.0.1:8000/
```

## Running Tests

Run all tests:

```bash
docker compose exec web python manage.py test
```

## Main User Flows

### Author

An authenticated user can:

- create a post;
- save it as a draft;
- publish it;
- edit their own posts;
- delete their own posts;
- manage posts from the "My posts" page.

### Anonymous User

An anonymous user can:

- view published posts;
- browse posts by category;
- browse posts by tag;
- view comments;
- register or log in.

### Staff User

A staff user can:

- access Django admin;
- manage posts, categories, comments, ratings, and profiles;
- edit or delete posts through site-level permissions where allowed.

## Notes

This project focuses on Django backend functionality, access control, user-generated content, and practical blog features.

The frontend uses Bootstrap with small custom styling to keep the interface clean and simple.

## License

This project is for portfolio and educational purposes.