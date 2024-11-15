# Operative Connect Lite - To-Do List

## Features & Functionality

* **Implement User Roles and Permissions:** Allow different levels of access within organizations (e.g., admin, member). This is crucial for data security and controlling access to sensitive information.
* **Search Functionality:** Add search capabilities to the organization and partnership lists for easier navigation and management, especially with larger datasets.
* **Partnership Details:** Allow viewing and managing details of a specific partnership, including adding/editing partnership attributes (e.g., status, dates).
* **UI Enhancements:** 
    * Add loading states during API calls
    * Improve error message display
    * Add form validation feedback
    * Add success/failure notifications
* **Testing:** 
    * Add unit tests for validation functions
    * Add integration tests for API endpoints
    * Set up test coverage reporting
* **API Documentation:** Generate and publish comprehensive API documentation (e.g., using Swagger/OpenAPI) to facilitate integration and understanding of the API.
* **Logging:** 
    * Add structured logging
    * Implement centralized logging solution
    * Add request/response logging middleware
* **Deployment Automation:**
    * Add environment-specific configurations
    * Implement staging environment
    * Add deployment verification tests

## Completed Items
* ✅ Data Validation: Implemented comprehensive input validation across all endpoints
* ✅ CORS Security: Restricted CORS to specific domains
* ✅ In-Memory Storage: Removed in favor of BigQuery storage
* ✅ Error Handling: Improved error messages and validation feedback
* ✅ Token Management: Implemented JWT token refresh mechanism

## Tech Debt
* **SQL Injection Prevention:** Review and update BigQuery queries to use parameterized queries
* **Token Security:** 
    * Add token blacklisting for logged out tokens
    * Implement token expiration cleanup
    * Add rate limiting for token refresh
* **Environment Variables:** Move all configuration to environment variables
* **Code Organization:** Split large files into smaller, focused modules