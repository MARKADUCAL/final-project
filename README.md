# AutoWash Hub API Documentation

This document provides information about the AutoWash Hub API endpoints and how to use them with Postman.

## Authentication

The API uses token-based authentication. You need to obtain a token by logging in before accessing protected endpoints.

### Base URL

All API endpoints are relative to the base URL of your deployment.

## API Endpoints

### Authentication Endpoints

#### 1. Register a new user

- **URL**: `/authentication/api/register/`
- **Method**: `POST`
- **Description**: Register a new user account
- **Request Body**:
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "password": "your_password",
    "confirm_password": "your_password"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Account created successfully",
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
  ```

#### 2. Login

- **URL**: `/authentication/api/login/`
- **Method**: `POST`
- **Description**: Login with existing credentials
- **Request Body**:
  ```json
  {
    "username": "johndoe",
    "password": "your_password"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Login successful",
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
  ```

#### 3. Get Authentication Token

- **URL**: `/authentication/api/token/`
- **Method**: `POST`
- **Description**: Get an authentication token for API access
- **Request Body**:
  ```json
  {
    "username": "johndoe",
    "password": "your_password"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "token": "abcdef123456",
    "user_id": 1,
    "username": "johndoe"
  }
  ```

#### 4. Check Authentication Status

- **URL**: `/authentication/api/auth-status/`
- **Method**: `GET`
- **Description**: Check if the current token is valid
- **Headers**:
  - `Authorization: Token abcdef123456`
- **Response**:
  ```json
  {
    "status": "success",
    "authenticated": true,
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com"
    }
  }
  ```

### Service Endpoints

#### 1. Get All Services

- **URL**: `/authentication/api/services/`
- **Method**: `GET`
- **Description**: Get a list of all available services
- **Headers**:
  - `Authorization: Token abcdef123456`
- **Response**:
  ```json
  {
    "status": "success",
    "services": [
      {
        "id": 1,
        "name": "Basic Wash",
        "description": "Exterior wash with soap and rinse",
        "price": 15.99,
        "duration_minutes": 30
      },
      {
        "id": 2,
        "name": "Premium Wash",
        "description": "Exterior wash, wax, and interior vacuum",
        "price": 29.99,
        "duration_minutes": 60
      }
    ]
  }
  ```

### Booking Endpoints

#### 1. Get All Bookings

- **URL**: `/authentication/api/bookings/`
- **Method**: `GET`
- **Description**: Get all bookings for the authenticated user
- **Headers**:
  - `Authorization: Token abcdef123456`
- **Response**:
  ```json
  {
    "status": "success",
    "bookings": [
      {
        "id": 1,
        "booking_id": "BK1A2B3",
        "service": "Basic Wash",
        "service_id": 1,
        "date_time": "2023-06-15 14:30",
        "status": "PENDING",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_type": "SEDAN",
        "license_plate": "ABC123",
        "additional_notes": "Please focus on the wheels",
        "price": 15.99,
        "created_at": "2023-06-10 09:15",
        "updated_at": "2023-06-10 09:15"
      }
    ]
  }
  ```

#### 2. Create a New Booking

- **URL**: `/authentication/api/bookings/create/`
- **Method**: `POST`
- **Description**: Create a new car wash booking
- **Headers**:
  - `Authorization: Token abcdef123456`
- **Request Body**:
  ```json
  {
    "service_id": 1,
    "date_time": "2023-06-15 14:30",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_type": "SEDAN",
    "license_plate": "ABC123",
    "additional_notes": "Please focus on the wheels"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Booking created successfully",
    "booking": {
      "id": 1,
      "booking_id": "BK1A2B3",
      "service": "Basic Wash",
      "date_time": "2023-06-15 14:30",
      "status": "PENDING",
      "price": 15.99
    }
  }
  ```

#### 3. Get Booking Details

- **URL**: `/authentication/api/bookings/{booking_id}/`
- **Method**: `GET`
- **Description**: Get details of a specific booking
- **Headers**:
  - `Authorization: Token abcdef123456`
- **Response**:
  ```json
  {
    "status": "success",
    "booking": {
      "id": 1,
      "booking_id": "BK1A2B3",
      "service": "Basic Wash",
      "service_id": 1,
      "date_time": "2023-06-15 14:30",
      "status": "PENDING",
      "vehicle_make": "Toyota",
      "vehicle_model": "Camry",
      "vehicle_type": "SEDAN",
      "license_plate": "ABC123",
      "additional_notes": "Please focus on the wheels",
      "price": 15.99,
      "created_at": "2023-06-10 09:15",
      "updated_at": "2023-06-10 09:15"
    }
  }
  ```

#### 4. Reschedule a Booking

- **URL**: `/authentication/api/bookings/{booking_id}/`
- **Method**: `PUT`
- **Description**: Reschedule an existing booking
- **Headers**:
  - `Authorization: Token abcdef123456`
- **Request Body**:
  ```json
  {
    "date_time": "2023-06-16 15:00"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Booking rescheduled successfully",
    "booking": {
      "id": 1,
      "booking_id": "BK1A2B3",
      "date_time": "2023-06-16 15:00",
      "status": "PENDING"
    }
  }
  ```

#### 5. Cancel a Booking

- **URL**: `/authentication/api/bookings/{booking_id}/`
- **Method**: `DELETE`
- **Description**: Cancel an existing booking
- **Headers**:
  - `Authorization: Token abcdef123456`
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Booking cancelled successfully"
  }
  ```

## Postman Examples

### Setting Up Postman for AutoWash Hub API

1. **Create a new collection** named "AutoWash Hub API"

2. **Set up environment variables**:

   - `base_url`: Your API base URL (e.g., `http://localhost:8000`)
   - `token`: Will store your authentication token

3. **Create a request for login**:

   - Method: POST
   - URL: `{{base_url}}/authentication/api/token/`
   - Body (raw JSON):
     ```json
     {
       "username": "your_username",
       "password": "your_password"
     }
     ```
   - Tests tab (to automatically set the token):
     ```javascript
     var jsonData = pm.response.json();
     if (jsonData.status === "success") {
       pm.environment.set("token", jsonData.token);
     }
     ```

4. **Create requests for other endpoints**:
   - For authenticated requests, add the Authorization header:
     - Key: `Authorization`
     - Value: `Token {{token}}`

### Example Workflow

1. Register a new user
2. Login and get token
3. Get available services
4. Create a new booking
5. View all bookings
6. Reschedule a booking
7. Cancel a booking

## Error Responses

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required or failed
- `404 Not Found`: Resource not found
- `405 Method Not Allowed`: HTTP method not supported

Error responses follow this format:

```json
{
  "status": "error",
  "message": "Description of the error"
}
```
