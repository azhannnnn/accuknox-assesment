# Social Networking API

This is a Django Rest Framework-based API for a social networking application. The API allows users to sign up, log in, search for other users, send and respond to friend requests, and list friends.

## Features

- User Signup
- User Login
- User Search by Email and Name
- Sending Friend Requests
- Responding to Friend Requests (Accept/Reject)
- Listing Friends
- Listing Pending Friend Requests
- Rate limiting on sending friend requests (max 3 per minute)

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (or any other database of your choice)

### Steps

1. **Clone the repository:**

    ```bash
    git clone https://github.com/azhannnnn/accuknox-assesment.git
    cd accuknox-assesment
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory with the following variables:

    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_URL=your_database_url
    ```

5. **Run database migrations:**

    ```bash
    python manage.py migrate
    ```

6. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## API Documentation

### Authentication

- **Signup:** `POST /signup/`
- **Login:** `POST /login/`

### User Management

- **Search Users:** `GET /search-users/?search=<query>`
- **Send Friend Request:** `POST /send-friend-request/`
- **Respond to Friend Request:** `PATCH /respond-to-friend-request/{id}/`
- **List Friends:** `GET /friends/`
- **Pending Friend Requests:** `GET /pending-requests/`


## Running Tests

To run the tests, use the following command:

```bash
python manage.py test
