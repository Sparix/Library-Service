# Library-Service

This application was designed to manage library data, providing details on books and borrowings.

# Features
#### User Registration:
- Users have the ability to register using their email and password.
#### Authentication with JWT:
- Authentication is implemented using JSON Web Tokens (JWT), providing a secure method for user verification.
#### Book Management:

- Users can browse a collection of books.
- Users can create new borrowings.
- Users can return borrowings.
#### Borrowing Filtering:

- Users have the capability to filter their borrowings based on their active status.
#### Admin Book Management:

- Admin users have a comprehensive CRUD (Create, Read, Update, Delete) implementation to manage books effectively.
#### Admin Borrowing Filtering:

- Admin users can filter all borrowings based on a specific user, allowing for efficient management.
#### Swagger UI Documentation:

- The application provides documentation through Swagger UI, offering a clear and interactive interface for understanding the API endpoints and functionality.

# Installation

To launch the application, follow next steps:

- Fork the repository

```shell
git clone https://github.com/Sparix/Library-Service
```

```
cd drf-library
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
```

Copy .env-sample -> .env and populate with all required data.

```shell
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
To run the tests: ``python manage.py test``
