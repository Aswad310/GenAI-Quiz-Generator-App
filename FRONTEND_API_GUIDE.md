# Quiz Generator App - Frontend Developer & AI Integration Guide

This document provides a comprehensive overview of the Backend API for the Quiz Generator App. It is designed to help Frontend developers and AI coding assistants understand the architecture, endpoints, and data flows required to build the application.

---

## 🚀 Overview

- **Backend Framework**: Django REST Framework (DRF)
- **Base URL**: `http://localhost:8000/api` (default development)
- **Authentication**: JWT (JSON Web Token) via Bearer Auth
- **Data Format**: JSON (Multipart/form-data for file uploads)

---

## 🔐 Authentication & Profile

### 1. User Sign Up
- **Endpoint**: `/registration/user-signup/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "user@example.com",
    "password": "strongpassword123",
    "confirm_password": "strongpassword123"
  }
  ```
- **Response**: Standardized response with `tokens` (refresh/access) inside `data`. OTP is sent to the email.

### 2. User Login
- **Endpoint**: `/registration/user-login/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123"
  }
  ```
- **Response**: Standardized response with `tokens` and `email_is_verified` status inside `data`.

### 3. OTP Verification
- **Endpoint**: `/registration/verify-otp/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access_token>`
- **Payload**:
  ```json
  {
    "otp_code": "123456"
  }
  ```

### 4. User Profile
- **Endpoint**: `/registration/user-detail/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: Standardized response with profile data (`first_name`, `last_name`, `email`) inside `data`.

### 5. Resend OTP
- **Endpoint**: `/registration/resend-otp/`
- **Method**: `POST`
- **Note**: Triggers a new OTP email if the previous one expired.

### 6. Password Reset Request
- **Endpoint**: `/registration/password-reset/`
- **Method**: `POST`
- **Payload**: `{ "email": "user@example.com" }`

### 7. Password Reset Confirm
- **Endpoint**: `/registration/password-reset-confirm/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "token": "uidb64-token-from-email",
    "password": "newpassword123",
    "confirm_password": "newpassword123"
  }
  ```

---

## 📄 Document Management

### 1. Upload Document
- **Endpoint**: `/documents/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Payload**:
  - `title`: String
  - `file`: .pdf, .docx, .txt etc.
- **Response**: Returns the created document object (UUID, title, file URL).

### 2. List Documents
- **Endpoint**: `/documents/`
- **Method**: `GET`
- **Response**: Paginated list of all uploaded documents for the current user.

### 3. Delete Document
- **Endpoint**: `/documents/<uuid:pk>/`
- **Method**: `DELETE`

---

## ⚙️ Configuration & LLM Settings

### 1. Get User Generation Config
- **Endpoint**: `/quizzes/settings/`
- **Method**: `GET`
- **Response**: Current user configuration (Selected LLM Model, temperature, etc.).

### 2. Update User Generation Config
- **Endpoint**: `/quizzes/settings/`
- **Method**: `PATCH`
- **Payload**:
  ```json
  {
    "model": "uuid-of-model",
    "temp": 0.5
  }
  ```

### 3. List Available LLM Models
- **Endpoint**: `/quizzes/models/`
- **Method**: `GET`
- **Response**: Paginated list of supported LLM models (e.g., GPT-4, Gemini 1.5).

### 4. Quiz Constants (Frontend Reference)
- **Difficulty Levels**: `Easy`, `Medium`, `High`
- **Max MCQs**: Currently recommended up to 50.

---

## 🧠 Quiz Generation

### 1. Generate Quiz
- **Endpoint**: `/quizzes/generate/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "document_id": "uuid-here",
    "number_of_mcqs": 10,
    "title": "History Quiz",
    "difficulty_level": "Medium" 
  }
  ```

---

## 📚 Quiz Library

### 1. List All Quizzes
- **Endpoint**: `/quizzes/`
- **Method**: `GET`
- **Response**: Returns a paginated list of all generated quizzes for the user.

### 2. Get Quiz Detail
- **Endpoint**: `/quizzes/<uuid:pk>/`
- **Method**: `GET`
- **Response**: Returns full quiz data, including all questions and options.

---

## 📝 Quiz Attempts

### 1. Start Attempt
- **Endpoint**: `/attempts/start/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "quiz_id": "uuid-here"
  }
  ```
- **Note**: If an active (unfinished) attempt exists, it resumes that instead of creating a new one.

### 2. Submit Answer
- **Endpoint**: `/attempts/<uuid:attempt_id>/submit-answer/`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "question_id": "uuid-here",
    "option_id": "uuid-here"
  }
  ```

### 3. Finish Attempt
- **Endpoint**: `/attempts/<uuid:attempt_id>/finish/`
- **Method**: `POST`
- **Payload**: `{}`
- **Response**: Returns total score and completion timestamp.

### 4. View Attempt Details (Results)
- **Endpoint**: `/attempts/<uuid:attempt_id>/`
- **Method**: `GET`
- **Response**: Complete attempt data, including user answers and correctness.

---

## 🛠️ Data Standards

### 1. Standard Success Response
All endpoints follow this structure:
```json
{
  "status": true,
  "message": "Description of action",
  "data": { ... } 
}
```

### 2. Paginated Response (List APIs)
Endpoints that return lists (Documents, Quizzes, Models) include navigation metadata and use the `results` key:
```json
{
  "status": true,
  "message": "Data fetched successfully.",
  "count": 45,
  "next": "http://api.yoursite.com/api/quizzes/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

### 3. Error Handling
Errors also follow a standardized structure matching the status codes (400, 401, 404, etc.):
```json
{
  "status": false,
  "message": "Validation failed / Not found / etc.",
  "data": { ... } // Contains field-specific errors if status is 400
}
```

---

## 🔄 Recommended UI Flow for FE

1.  **Auth**: Login/Signup -> Redirect to Dashboard.
2.  **Dashboard**: Show list of uploaded documents and recent quizzes.
3.  **Upload**: Provide a file dropzone -> Call `POST /documents/`.
4.  **Generation**: User selects document -> Configures MCQ count/difficulty -> Call `POST /quizzes/generate/`.
5.  **Quiz Detail**: Show generated questions (read-only) or "Start Quiz" button.
6.  **Quiz Play**:
    - Call `POST /attempts/start/`.
    - Loop through questions: User selects option -> `POST /submit-answer/`.
    - User clicks "Finish" -> `POST /finish/`.
7.  **Results**: Show score and highlight correct/incorrect answers.
