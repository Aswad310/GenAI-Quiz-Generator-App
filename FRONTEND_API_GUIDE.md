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
- **Response**: Returns `tokens` (refresh/access) and a `message`. OTP is sent to the email.

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
- **Response**: Returns `tokens`, `email_is_verified` status, and `message`.

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
- **Response**: Returns current user's profile (`first_name`, `last_name`, `email`).

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
- **Response**: List of all uploaded documents for the current user.

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
- **Response**: List of supported LLM models (e.g., GPT-4, Gemini 1.5).

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
- **Response**: Returns a list of all generated quizzes for the user.

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

### Common Success Response Format
Most endpoints (except registration) follow this structure:
```json
{
  "message": "Action successful",
  "status": true,
  "data": { ... }
}
```

### Error Handling
Errors are returned with appropriate HTTP status codes (400, 401, 403, 404) and usually follow this structure:
```json
{
  "message": "Specific error description here"
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
