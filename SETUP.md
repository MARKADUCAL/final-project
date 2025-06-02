# AutoWash Hub - Setup Guide

This guide will help you set up and run the AutoWash Hub project locally.

## Prerequisites

- Python 3.8+ installed
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation

1. Clone the repository (if not already done):

   ```
   git clone https://github.com/MARKADUCAL/finalproject.git
   cd autowash-hub
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root with the following variables:

   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///db.sqlite3
   ```

2. Run database migrations:

   ```
   python manage.py migrate
   ```

3. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```

## Running the Server

1. Start the development server:

   ```
   python manage.py runserver
   ```

2. Access the application:
   - API: http://localhost:8000/
   - Admin interface: http://localhost:8000/admin/

## Testing the API

You can test the API endpoints using Postman as described in the [API Documentation](README.md).

1. Register a new user
2. Obtain an authentication token
3. Use the token to access protected endpoints

## Troubleshooting

- If you encounter any package-related errors, ensure your virtual environment is activated and all dependencies are installed.
- For database errors, try deleting the db.sqlite3 file and running migrations again.
- Check the console output for specific error messages.

## Development

For development purposes, you can load sample data:

```
python manage.py loaddata sample_data.json
```

This will create sample services and bookings for testing.
