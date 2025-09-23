# EventSphere API Endpoints Documentation

## 📋 Overview

This document provides comprehensive documentation for all EventSphere API endpoints. The API is organized into **Admin** and **Public** sections, with clear categorization for easy frontend integration.

### 🔐 Authentication
- **Admin Endpoints**: Require JWT token with admin/organizer role
- **Public Endpoints**: May require authentication for certain operations
- **Bearer Token**: `Authorization: Bearer <jwt_token>`

### 📊 Response Format
All endpoints return JSON responses with consistent structure:
```json
{
  "status": "success|failed",
  "status_code": 200,
  "message": "Response message",
  "data": { /* Response data */ }
}
```

### 📎 Request Formats
The API supports multiple request formats for different use cases:

#### **JSON Requests** (Default)
```http
Content-Type: application/json
```
- Standard JSON request/response format
- Used for most API operations
- Suitable for text-based data

#### **FormData Requests** (File Uploads)
```http
Content-Type: multipart/form-data
```
- Used for file uploads (images, documents)
- Automatically detected by API endpoints
- Supports both text fields and file uploads
- Used by Event Management endpoints for image uploads

**FormData Example:**
```javascript
const formData = new FormData();
formData.append('title', 'Event Title');
formData.append('image', imageFile);

fetch('/api/v1/admin/events', {
  method: 'POST',
  body: formData
});
```

---

# 🛡️ ADMIN ENDPOINTS


## 👥 User Management

### Get User Statistics
```http
GET /api/v1/admin/users/stats
```
- **Description**: Get comprehensive user statistics for admin dashboard
- **Auth Required**: Admin token
- **Response**:
```json
{
  "total_users": 150,
  "active_users": 145,
  "inactive_users": 5,
  "admin_users": 3,
  "organizer_users": 12,
  "participant_users": 89,
  "visitor_users": 46,
  "recent_registrations": 15
}
```

### List Users
```http
GET /api/v1/admin/users?page=1&per_page=20&role_filter=Participant&search=john
```
- **Description**: List users with pagination and filtering
- **Auth Required**: Admin token
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20, max: 100)
  - `role_filter` (string): Filter by role (Admin, Organizer, Participant, Visitor)
  - `status_filter` (string): Filter by status (active, inactive)
  - `search` (string): Search in username, email, firstname, lastname
- **Response**:
```json
{
  "users": [
    {
      "id": "uuid",
      "username": "john_doe",
      "email": "john@example.com",
      "firstname": "John",
      "lastname": "Doe",
      "date_joined": "2024-01-15 10:30:00",
      "roles": ["Participant"],
      "is_active": true
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8
}
```

### Get User Details
```http
GET /api/v1/admin/users/{user_id}
```
- **Description**: Get detailed information about a specific user
- **Auth Required**: Admin token
- **Path Parameters**:
  - `user_id` (string): User UUID
- **Response**:
```json
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "date_joined": "2024-01-15 10:30:00",
  "profile": {
    "firstname": "John",
    "lastname": "Doe",
    "phone": "+1234567890",
    "gender": "Male",
    "enrollment_no": "EN2024001",
    "department": "Computer Science"
  },
  "address": {
    "country": "Nigeria",
    "state": "Lagos"
  },
  "roles": ["Participant"],
  "is_active": true
}
```

### Update User Roles
```http
PATCH /api/v1/admin/users/{user_id}/roles
```
- **Description**: Add or remove roles from a user
- **Auth Required**: Admin token
- **Path Parameters**:
  - `user_id` (string): User UUID
- **Request Body**:
```json
{
  "roles_to_add": ["Organizer"],
  "roles_to_remove": ["Participant"]
}
```
- **Response**:
```json
{
  "roles": ["Organizer"]
}
```

### Update User Status
```http
PATCH /api/v1/admin/users/{user_id}/status
```
- **Description**: Activate or deactivate a user account
- **Auth Required**: Admin token
- **Path Parameters**:
  - `user_id` (string): User UUID
- **Request Body**:
```json
{
  "is_active": false
}
```
- **Response**:
```json
{
  "user_id": "uuid",
  "is_active": false
}
```

### Update User Profile
```http
PATCH /api/v1/admin/users/{user_id}/profile
```
- **Description**: Update user's profile information
- **Auth Required**: Admin token
- **Path Parameters**:
  - `user_id` (string): User UUID
- **Request Body**:
```json
{
  "firstname": "John",
  "lastname": "Smith",
  "phone": "+1234567890",
  "gender": "Male",
  "enrollment_no": "EN2024001",
  "department": "Computer Science"
}
```
- **Response**:
```json
{
  "profile": {
    "firstname": "John",
    "lastname": "Smith",
    "phone": "+1234567890",
    "gender": "Male",
    "enrollment_no": "EN2024001",
    "department": "Computer Science"
  }
}
```

### Update User Address
```http
PATCH /api/v1/admin/users/{user_id}/address
```
- **Description**: Update user's address information
- **Auth Required**: Admin token
- **Path Parameters**:
  - `user_id` (string): User UUID
- **Request Body**:
```json
{
  "country": "Nigeria",
  "state": "Lagos"
}
```
- **Response**:
```json
{
  "address": {
    "country": "Nigeria",
    "state": "Lagos"
  }
}
```

---

## 🎪 Event Management

### Create Event

#### 🎯 **Method 1: JSON Request (URLs Only)**
```http
POST /api/v1/admin/events
Content-Type: application/json
```
- **Description**: Create a new event with image URLs (Organizer/Admin only)
- **Auth Required**: Admin or Organizer token
- **Request Body**:
```json
{
  "title": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-12-15",
  "time": "09:00:00",
  "venue": "Convention Center",
  "capacity": 500,
  "max_participants": 450,
  "category_id": "uuid",
  "featured_image_url": "https://cloudinary.com/.../featured.jpg",
  "gallery_image_urls": [
    "https://cloudinary.com/.../image1.jpg",
    "https://cloudinary.com/.../image2.jpg",
    "https://cloudinary.com/.../image3.jpg"
  ]
}
```

#### 🎯 **Method 2: FormData Request (File Uploads)**
```http
POST /api/v1/admin/events
Content-Type: multipart/form-data
```
- **Description**: Create a new event with actual image file uploads (Organizer/Admin only)
- **Auth Required**: Admin or Organizer token
- **Form Fields**:
  - `title` (string, required): Event title
  - `description` (string, required): Event description
  - `date` (string, required): ISO format date (YYYY-MM-DD)
  - `time` (string, required): ISO format time (HH:MM:SS)
  - `venue` (string, required): Event venue
  - `capacity` (number, required): Maximum capacity (0 for unlimited)
  - `max_participants` (number, required): Maximum participants (0 for unlimited)
  - `category_id` (string, optional): Event category UUID as string
  - `featured_image` (file, optional): Featured image file (JPEG, PNG, etc.)
  - `gallery_images[]` (file[], optional): Gallery image files (multiple files allowed)

**Example FormData Request:**
```javascript
const formData = new FormData();
formData.append('title', 'Tech Conference 2024');
formData.append('description', 'Annual technology conference');
formData.append('date', '2024-12-15');
formData.append('time', '09:00:00');
formData.append('venue', 'Convention Center');
formData.append('capacity', '500');
formData.append('max_participants', '450');
formData.append('category_id', '550e8400-e29b-41d4-a716-446655440000');

// Add featured image
formData.append('featured_image', featuredImageFile);

// Add gallery images
galleryImageFiles.forEach((file, index) => {
  formData.append('gallery_images[]', file);
});

fetch('/api/v1/admin/events', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + jwtToken
  },
  body: formData
});
```

**FormData Response with Upload Status:**
```json
{
  "status": "success",
  "status_code": 201,
  "message": "Event created successfully with image uploads. Images are processing in background.",
  "data": {
    "event": {
      "id": "uuid",
      "title": "Tech Conference 2024",
      // ... other event fields
      "upload_status": {
        "featured_image": "uploading:event_uuid_featured_abc123.jpg",
        "gallery_images": [
          "uploading:event_uuid_gallery_0_def456.jpg",
          "uploading:event_uuid_gallery_1_ghi789.jpg"
        ],
        "message": "Images are being uploaded to Cloudinary in the background"
      }
    }
  }
}
```

- **Upload Processing**: Images are uploaded to Cloudinary in background threads
- **Status Tracking**: Response includes upload status for tracking progress
- **Supported Formats**: JPEG, PNG, GIF, WebP
- **File Size Limit**: 10MB per image (configurable)
- **Background Processing**: API responds immediately while uploads continue

- **Response**: Event object with generated ID including featured and gallery images
- **Image Response Format**:
```json
{
  "featured_image": {
    "id": "uuid",
    "url": "https://cloudinary.com/.../featured.jpg",
    "thumbnail_url": "https://cloudinary.com/.../thumb_featured.jpg",
    "filename": "featured.jpg",
    "width": 1920,
    "height": 1080
  },
  "gallery_images": [
    {
      "id": "uuid",
      "url": "https://cloudinary.com/.../image1.jpg",
      "thumbnail_url": "https://cloudinary.com/.../thumb_image1.jpg",
      "filename": "image1.jpg",
      "width": 800,
      "height": 600,
      "file_type": "image",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```
- **Note**: Featured image and gallery images are now fully functional and included in all event responses.

### List Events (Admin)
```http
GET /api/v1/admin/events?page=1&per_page=20&status=pending&organizer_id=uuid&search=conference
```
- **Description**: Get paginated list of all events with filtering
- **Auth Required**: Admin or Organizer token
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20)
  - `status` (string): Filter by status (pending, approved, cancelled)
  - `organizer_id` (string): Filter by organizer ID
  - `search` (string): Search in title, description, venue
- **Response**: Paginated event list

### Get Event Details (Admin)
```http
GET /api/v1/admin/events/{event_id}
```
- **Description**: Get detailed information about a specific event
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Response**: Complete event object with organizer details, featured image, and gallery images (now fully functional)

### Update Event

#### 🎯 **Method 1: JSON Request (URLs Only)**
```http
PUT /api/v1/admin/events/{event_id}
Content-Type: application/json
```
- **Description**: Update an existing event with image URLs (Organizer/Admin only)
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**: Same as create event (all fields optional). Includes optional image fields:
  - `featured_image_url`: URL of the featured image
  - `gallery_image_urls`: Array of gallery image URLs

#### 🎯 **Method 2: FormData Request (File Uploads)**
```http
PUT /api/v1/admin/events/{event_id}
Content-Type: multipart/form-data
```
- **Description**: Update an existing event with actual image file uploads (Organizer/Admin only)
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Form Fields**: Same as create event FormData (all fields optional)
  - `title` (string, optional): Event title
  - `description` (string, optional): Event description
  - `date` (string, optional): ISO format date (YYYY-MM-DD)
  - `time` (string, optional): ISO format time (HH:MM:SS)
  - `venue` (string, optional): Event venue
  - `capacity` (number, optional): Maximum capacity
  - `max_participants` (number, optional): Maximum participants
  - `category_id` (string, optional): Event category UUID as string
  - `featured_image` (file, optional): New featured image file
  - `gallery_images[]` (file[], optional): New gallery image files

**FormData Update Example:**
```javascript
const formData = new FormData();
formData.append('title', 'Updated Tech Conference 2024');
formData.append('venue', 'New Convention Center');

// Add new featured image (replaces existing)
formData.append('featured_image', newFeaturedImageFile);

// Add additional gallery images (appends to existing)
additionalGalleryFiles.forEach((file, index) => {
  formData.append('gallery_images[]', file);
});

fetch(`/api/v1/admin/events/${eventId}`, {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer ' + jwtToken
  },
  body: formData
});
```

- **Response**: Updated event object with featured and gallery images (now fully functional)
- **Upload Processing**: Same background processing as create event
- **Note**: Only provided images will be uploaded; existing images remain unchanged unless replaced

### Delete Event
```http
DELETE /api/v1/admin/events/{event_id}
```
- **Description**: Delete an event (Organizer/Admin only)
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Response**: Success confirmation

### Approve Event
```http
POST /api/v1/admin/events/{event_id}/approve
```
- **Description**: Approve a pending event (Admin only)
- **Auth Required**: Admin token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**: Empty or approval metadata
- **Response**: Success confirmation

### Publish/Unpublish Event
```http
POST /api/v1/admin/events/{event_id}/publish
```
- **Description**: Toggle publish status of an approved event
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**: Empty (toggles current status)
- **Response**: Success confirmation

---

## 📊 Attendance Management

### Mark Attendance
```http
POST /api/v1/admin/events/{event_id}/attendance
```
- **Description**: Mark attendance for event participants
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**:
```json
{
  "user_id": "uuid",
  "attended": true
}
```
- **Response**: Attendance record confirmation

### Get Event Attendance
```http
GET /api/v1/admin/events/{event_id}/attendance
```
- **Description**: Get attendance records for an event
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20)
- **Response**:
```json
{
  "event_id": "uuid",
  "total_registered": 150,
  "total_attended": 142,
  "attendance_rate": 94.7,
  "attendees": [
    {
      "user_id": "uuid",
      "username": "john_doe",
      "fullname": "John Doe",
      "attended": true,
      "marked_at": "2024-01-15 10:30:00"
    }
  ]
}
```

---

## 🏆 Certificate Management

### Generate Certificate
```http
POST /api/v1/admin/events/{event_id}/certificates
```
- **Description**: Generate certificate for event participant
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**:
```json
{
  "user_id": "uuid"
}
```
- **Response**: Certificate generation confirmation

### Bulk Generate Certificates
```http
POST /api/v1/admin/events/{event_id}/certificates/bulk
```
- **Description**: Generate certificates for multiple participants
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**:
```json
{
  "user_ids": ["uuid1", "uuid2", "uuid3"]
}
```
- **Response**: Bulk generation status

### Get Event Certificates
```http
GET /api/v1/admin/events/{event_id}/certificates
```
- **Description**: Get all certificates for an event
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20)
- **Response**: List of certificates with download URLs

---

## ⭐ Feedback Management

### Get Event Feedback
```http
GET /api/v1/admin/events/{event_id}/feedback
```
- **Description**: Get feedback for a specific event
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20)
- **Response**:
```json
{
  "event_id": "uuid",
  "total_feedback": 45,
  "average_rating": 4.2,
  "feedback": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "username": "john_doe",
      "rating": 5,
      "comment": "Excellent event!",
      "aspects": {
        "venue": 5,
        "coordination": 4,
        "content": 5
      },
      "submitted_at": "2024-01-15 15:30:00"
    }
  ]
}
```

### Get Feedback Statistics
```http
GET /api/v1/admin/events/{event_id}/feedback/stats
```
- **Description**: Get feedback analytics and statistics
- **Auth Required**: Admin or Organizer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Response**:
```json
{
  "event_id": "uuid",
  "total_responses": 45,
  "average_rating": 4.2,
  "rating_distribution": {
    "5": 20,
    "4": 15,
    "3": 8,
    "2": 2,
    "1": 0
  },
  "aspect_averages": {
    "venue": 4.3,
    "coordination": 4.1,
    "content": 4.4,
    "speakers": 4.0
  }
}
```

---

# 🌐 PUBLIC ENDPOINTS

## 🔐 Authentication

### User Registration
```http
POST /api/v1/auth/signup
```
- **Description**: Register a new user account
- **Auth Required**: None
- **Request Body**:
```json
{
  "email": "user@example.com",
  "firstname": "John",
  "lastname": "Doe",
  "username": "johndoe",
  "password": "securepassword123"
}
```
- **Response**: Registration confirmation with verification instructions

### User Login
```http
POST /api/v1/auth/login
```
- **Description**: Authenticate user and get JWT token
- **Auth Required**: None
- **Request Body**:
```json
{
  "email_username": "user@example.com",
  "password": "securepassword123"
}
```
- **Response**:
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "username": "johndoe",
    "email": "user@example.com",
    "roles": ["Participant"]
  }
}
```

### Email Verification
```http
POST /api/v1/auth/verify-email
```
- **Description**: Verify user email with verification code
- **Auth Required**: None
- **Request Body**:
```json
{
  "reg_id": "registration_id_from_email",
  "code": "123456"
}
```
- **Response**: Verification confirmation

### Resend Verification Code
```http
POST /api/v1/auth/resend-code
```
- **Description**: Resend email verification code
- **Auth Required**: None
- **Request Body**:
```json
{
  "reg_id": "registration_id_from_email"
}
```
- **Response**: Code resend confirmation

### Validate Token
```http
POST /api/v1/auth/validate-token
```
- **Description**: Validate JWT token and get user info
- **Auth Required**: Bearer token
- **Request Body**:
```json
{
  "token": "jwt_token_here"
}
```
- **Response**: Token validation result with user data

### Refresh Token
```http
POST /api/v1/auth/refresh-token
```
- **Description**: Refresh expired JWT token
- **Auth Required**: Valid refresh token
- **Request Body**:
```json
{
  "token": "refresh_token_here"
}
```
- **Response**: New access token

### Check Email Availability
```http
POST /api/v1/auth/check-email
```
- **Description**: Check if email is available for registration
- **Auth Required**: None
- **Request Body**:
```json
{
  "email": "user@example.com"
}
```
- **Response**:
```json
{
  "available": true,
  "message": "Email is available"
}
```

### Check Username Availability
```http
POST /api/v1/auth/check-username
```
- **Description**: Check if username is available for registration
- **Auth Required**: None
- **Request Body**:
```json
{
  "username": "johndoe"
}
```
- **Response**:
```json
{
  "available": false,
  "message": "Username is already taken"
}
```

### Request Password Reset
```http
POST /api/v1/auth/forgot-password
```
- **Description**: Request a password reset link to be sent to email address
- **Auth Required**: None
- **Rate Limited**: 3 requests per 15 minutes per email
- **Request Body**:
```json
{
  "email": "user@example.com"
}
```
- **Response**: Always returns success (prevents email enumeration)
```json
{
  "message": "If an account with this email exists, a password reset link has been sent."
}
```
- **Security Notes**:
  - Always returns success regardless of email existence
  - Rate limited to prevent spam
  - Reset link expires in 30 minutes

### Validate Password Reset Token
```http
GET /api/v1/auth/pwd-reset-token?token=jwt_reset_token
```
- **Description**: Validate password reset token before showing reset form
- **Auth Required**: None
- **Query Parameters**:
  - `token` (string, required): JWT password reset token from email
- **Response**:
```json
{
  "valid": true,
  "expires_at": 1640995200
}
```
- **Error Responses**:
  - `400`: Invalid or expired token
  - `429`: Too many validation attempts

### Reset Password
```http
POST /api/v1/auth/reset-password
```
- **Description**: Reset user password using valid reset token
- **Auth Required**: None
- **Request Body**:
```json
{
  "token": "jwt_reset_token_from_email",
  "new_password": "new_secure_password123"
}
```
- **Response**:
```json
{
  "message": "Password has been reset successfully"
}
```
- **Security Notes**:
  - Token is invalidated after successful reset
  - Max 3 reset attempts per token
  - Password must be at least 6 characters

---

## 🎪 Event Discovery

### List Public Events
```http
GET /api/v1/events?page=1&per_page=20&category_id=uuid&search=conference
```
- **Description**: Get paginated list of approved and published events
- **Auth Required**: None (optional for authenticated features)
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20)
  - `category_id` (string): Filter by category UUID
  - `search` (string): Search in title, description, venue
- **Response**: Paginated list of public events

### Get Event Details (Public)
```http
GET /api/v1/events/{event_id}
```
- **Description**: Get detailed information about a public event
- **Auth Required**: None
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Response**: Complete event object (public information only) with featured image and gallery images (now fully functional)

### Get Event Categories
```http
GET /api/v1/events/categories
```
- **Description**: Get list of all event categories
- **Auth Required**: None
- **Response**:
```json
{
  "categories": [
    {
      "id": "uuid",
      "name": "Technology",
      "description": "Tech conferences and workshops"
    }
  ]
}
```

---

## 👥 Registration Management

### Register for Event
```http
POST /api/v1/events/{event_id}/register
```
- **Description**: Register current user for an event
- **Auth Required**: Bearer token (Participant/Visitor)
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**: Empty (registration uses current user)
- **Response**: Registration confirmation with details

### Cancel Registration
```http
DELETE /api/v1/events/{event_id}/register
```
- **Description**: Cancel user's registration for an event
- **Auth Required**: Bearer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Response**: Cancellation confirmation

### Get User Registrations
```http
GET /api/v1/user/registrations?page=1&per_page=20
```
- **Description**: Get current user's event registrations
- **Auth Required**: Bearer token
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20)
- **Response**: List of user's registrations with event details

### Get Registration Details
```http
GET /api/v1/events/{event_id}/registration
```
- **Description**: Get user's registration details for specific event
- **Auth Required**: Bearer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Response**: Registration details including status and timestamps

---

## 🏆 Certificate Access

### Download Certificate
```http
GET /api/v1/certificates/{certificate_id}/download
```
- **Description**: Download user's earned certificate
- **Auth Required**: Bearer token (certificate owner)
- **Path Parameters**:
  - `certificate_id` (string): Certificate UUID
- **Query Parameters**:
  - `format` (string): Download format (pdf, png) - default: pdf
- **Response**: Certificate file download

### Get User Certificates
```http
GET /api/v1/user/certificates?page=1&per_page=20
```
- **Description**: Get current user's certificates
- **Auth Required**: Bearer token
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20)
- **Response**:
```json
{
  "certificates": [
    {
      "id": "uuid",
      "event_id": "uuid",
      "event_title": "Tech Conference 2024",
      "issued_at": "2024-01-15 15:30:00",
      "download_url": "/api/v1/certificates/uuid/download",
      "certificate_number": "CERT-2024-001"
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 20
}
```

---

## ⭐ Feedback System

### Submit Feedback
```http
POST /api/v1/events/{event_id}/feedback
```
- **Description**: Submit feedback for attended event
- **Auth Required**: Bearer token (attendee only)
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**:
```json
{
  "rating": 5,
  "comment": "Excellent event with great speakers!",
  "aspects": {
    "venue": 5,
    "coordination": 4,
    "content": 5,
    "speakers": 5
  }
}
```
- **Response**: Feedback submission confirmation

### Get User Feedback
```http
GET /api/v1/user/feedback?page=1&per_page=20
```
- **Description**: Get current user's submitted feedback
- **Auth Required**: Bearer token
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (default: 20)
- **Response**: List of user's feedback submissions

### Update Feedback
```http
PUT /api/v1/feedback/{feedback_id}
```
- **Description**: Update user's existing feedback
- **Auth Required**: Bearer token (feedback owner only)
- **Path Parameters**:
  - `feedback_id` (string): Feedback UUID
- **Request Body**: Same as submit feedback
- **Response**: Updated feedback confirmation

### Delete Feedback
```http
DELETE /api/v1/feedback/{feedback_id}
```
- **Description**: Delete user's feedback
- **Auth Required**: Bearer token (feedback owner only)
- **Path Parameters**:
  - `feedback_id` (string): Feedback UUID
- **Response**: Deletion confirmation

---

## 📁 Admin Media Management

### Upload Event Media
```http
POST /api/v1/admin/events/{event_id}/media/upload
```
- **Description**: Upload media files to an event (Admin/Organizer only)
- **Auth Required**: Admin Bearer token
- **Content-Type**: `multipart/form-data`
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Form Data**:
  - `files`: Media files (multiple allowed)
  - `custom_filename` (optional): Custom filename for uploaded files
  - `optimize` (boolean, optional): Enable/disable image optimization (default: true)
- **Response**:
```json
{
  "status": "success",
  "status_code": 201,
  "message": "Successfully uploaded 2 file(s)",
  "data": {
    "uploaded": [
      {
        "id": "uuid",
        "filename": "image.jpg",
        "original_filename": "original.jpg",
        "file_type": "image",
        "file_size": 1024000,
        "cloudinary_url": "https://cloudinary.com/...",
        "is_featured": false,
        "uploaded_at": "2024-01-15T10:30:00Z"
      }
    ],
    "errors": []
  }
}
```

### List Event Media
```http
GET /api/v1/admin/events/{event_id}/media?page=1&per_page=20
```
- **Description**: Get paginated list of media files within an event (Admin/Organizer only)
- **Auth Required**: Admin Bearer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (max: 50, default: 20)
  - `file_type` (string): Filter by file type (image, video, document)
  - `is_featured` (boolean): Filter by featured media only
  - `search` (string): Search in filenames
  - `sort` (string): Sort order (created_at, filename, file_size) (default: created_at)
  - `order` (string): Sort direction (asc, desc) (default: desc)
- **Response**: Paginated list of event media files

### Get Event Media Details
```http
GET /api/v1/admin/events/{event_id}/media/{media_id}
```
- **Description**: Get detailed information about a specific media file (Admin/Organizer only)
- **Auth Required**: Admin Bearer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
  - `media_id` (string): Media UUID
- **Response**: Media metadata and access URLs

### Update Event Media
```http
PUT /api/v1/admin/events/{event_id}/media/{media_id}
```
- **Description**: Update media metadata (Admin/Organizer only)
- **Auth Required**: Admin Bearer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
  - `media_id` (string): Media UUID
- **Request Body**:
```json
{
  "filename": "new_filename.jpg",
  "is_featured": true
}
```
- **Response**: Updated media information

### Delete Event Media
```http
DELETE /api/v1/admin/events/{event_id}/media/{media_id}
```
- **Description**: Delete a media file (Admin/Organizer only)
- **Auth Required**: Admin Bearer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
  - `media_id` (string): Media UUID
- **Response**: Deletion confirmation

### Bulk Delete Event Media
```http
POST /api/v1/admin/events/{event_id}/media/bulk-delete
```
- **Description**: Delete multiple media files in a single request (Admin/Organizer only)
- **Auth Required**: Admin Bearer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Request Body**:
```json
{
  "media_ids": ["uuid1", "uuid2", "uuid3"]
}
```
- **Response**:
```json
{
  "status": "success",
  "status_code": 200,
  "message": "Successfully deleted 3 file(s)",
  "data": {
    "deleted_count": 3,
    "failed_deletions": []
  }
}
```

### Get Event Media Statistics
```http
GET /api/v1/admin/events/{event_id}/media/stats?period=month
```
- **Description**: Get media statistics for an event (Admin/Organizer only)
- **Auth Required**: Admin Bearer token
- **Path Parameters**:
  - `event_id` (string): Event UUID
- **Query Parameters**:
  - `period` (string): Time period for stats (day, week, month, year) (default: month)
- **Response**:
```json
{
  "status": "success",
  "status_code": 200,
  "message": "Media statistics retrieved successfully",
  "data": {
    "total_files": 25,
    "total_size": 52428800,
    "total_size_mb": 50.0,
    "by_type": {
      "image": 20,
      "document": 3,
      "video": 2
    }
  }
}
```

## 📁 Public Media Access

### Get Public Event Media
```http
GET /api/v1/events/public/{handle}/media?page=1&per_page=20
```
- **Description**: Get media files for a public event by handle (No authentication required)
- **Auth Required**: None
- **Path Parameters**:
  - `handle` (string): Event handle
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `per_page` (integer): Items per page (max: 50, default: 20)
  - `file_type` (string): Filter by file type (image, video, document)
  - `is_featured` (boolean): Show only featured media
- **Response**: Paginated list of public event media files

---

## 📊 Error Responses

### Common Error Codes
- **400 Bad Request**: Invalid request data or validation error
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions for operation
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (duplicate, already exists)
- **422 Unprocessable Entity**: Validation failed
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Error Response Format
```json
{
  "status": "failed",
  "status_code": 400,
  "message": "Validation error: email is required",
  "data": {
    "field": "email",
    "error": "field_required"
  }
}
```

---

## 🔧 Development Notes

### Rate Limiting
- Authentication endpoints: 5 requests per minute
- General endpoints: 100 requests per minute
- File uploads: 10 requests per minute

### Pagination
- Default page size: 20 items
- Maximum page size: 100 items
- Zero-based indexing: false (pages start at 1)

### File Upload Limits
- Maximum file size: 10MB
- Supported formats: Images (jpg, png, gif), Documents (pdf, doc, docx)
- Storage: Cloudinary CDN with automatic optimization

### CORS Policy
- Origins: Configurable per environment
- Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
- Headers: Content-Type, Authorization, Origin
- Credentials: Supported for authenticated requests

---

## 🎯 Quick Reference

### Most Used Endpoints
1. `POST /api/v1/auth/login` - User authentication
2. `GET /api/v1/events` - Browse events
3. `POST /api/v1/events/{id}/register` - Register for events
4. `GET /api/v1/user/certificates` - Access certificates
5. `POST /api/v1/events/{id}/feedback` - Submit feedback

### Admin Dashboard Endpoints
1. `GET /api/v1/admin/users/stats` - User statistics
2. `GET /api/v1/admin/events` - Manage events
3. `GET /api/v1/admin/events/{id}/attendance` - Track attendance
4. `POST /api/v1/admin/events/{id}/certificates/bulk` - Generate certificates
5. `GET /api/v1/admin/events/{id}/feedback/stats` - View analytics

This documentation covers all implemented endpoints as of the current EventSphere MVP (70% complete). For the latest updates, check the API documentation at `/apidoc/swagger`.
