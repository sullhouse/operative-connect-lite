# Error Codes

This document lists and describes all the standardized error codes used across the API endpoints.

## Error Codes

### UNAUTHORIZED
- **Code:** `UNAUTHORIZED`
- **Message:** Unauthorized
- **Description:** The request requires user authentication. The user is not authorized to access the resource.

### INVALID_REQUEST
- **Code:** `INVALID_REQUEST`
- **Message:** Invalid request format or data
- **Description:** The request data format is invalid or missing required fields.

### INVALID_ORGANIZATION_NAME
- **Code:** `INVALID_ORGANIZATION_NAME`
- **Message:** Invalid organization name
- **Description:** The organization name does not meet the required format or length constraints.

### ORGANIZATION_EXISTS
- **Code:** `ORGANIZATION_EXISTS`
- **Message:** Organization name already exists
- **Description:** The organization name already exists in the database.

### INTERNAL_ERROR
- **Code:** `INTERNAL_ERROR`
- **Message:** Internal server error
- **Description:** An unexpected error occurred on the server.

### INVALID_ORGANIZATION_ID
- **Code:** `INVALID_ORGANIZATION_ID`
- **Message:** Both organization IDs are required
- **Description:** One or both organization IDs are missing or invalid.

### INVALID_UUID
- **Code:** `INVALID_UUID`
- **Message:** Invalid UUID format
- **Description:** The provided UUID format is invalid.

### ORGANIZATION_NOT_FOUND
- **Code:** `ORGANIZATION_NOT_FOUND`
- **Message:** One or both organizations do not exist
- **Description:** One or both of the specified organizations do not exist in the database.

### PARTNERSHIP_EXISTS
- **Code:** `PARTNERSHIP_EXISTS`
- **Message:** Partnership already exists between these organizations
- **Description:** A partnership already exists between the specified organizations.

### NOT_FOUND
- **Code:** `NOT_FOUND`
- **Message:** Function not found
- **Description:** The requested function does not exist.

### INVALID_USERNAME
- **Code:** `INVALID_USERNAME`
- **Message:** Invalid username
- **Description:** The username does not meet the required format or length constraints.

### INVALID_PASSWORD
- **Code:** `INVALID_PASSWORD`
- **Message:** Invalid password
- **Description:** The password does not meet the required strength or format constraints.

### USERNAME_EXISTS
- **Code:** `USERNAME_EXISTS`
- **Message:** Username already exists
- **Description:** The username already exists in the database.

### INVALID_CREDENTIALS
- **Code:** `INVALID_CREDENTIALS`
- **Message:** Invalid credentials
- **Description:** The provided username or password is incorrect.

### INVALID_TOKEN
- **Code:** `INVALID_TOKEN`
- **Message:** Invalid token
- **Description:** The provided JWT token is invalid or expired.

### TOKEN_VALIDATION_ERROR
- **Code:** `TOKEN_VALIDATION_ERROR`
- **Message:** Token validation error
- **Description:** An error occurred while validating the JWT token.