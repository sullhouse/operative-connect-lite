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
* **User Activity Tracking:** Implement tracking of user activities for auditing purposes
* **Data Export:** Add functionality to export data in CSV and JSON formats

## Completed Items
* ✅ Data Validation: Implemented comprehensive input validation across all endpoints
* ✅ CORS Security: Restricted CORS to specific domains
* ✅ In-Memory Storage: Removed in favor of BigQuery storage
* ✅ Error Handling: Improved error messages and validation feedback
* ✅ Token Management: Implemented JWT token refresh mechanism
* ✅ Shortened Unique IDs: Updated ID generation to use 6-character unique IDs without dashes
* ✅ SQL Injection Prevention: Reviewed and updated BigQuery queries to use parameterized queries
* ✅ Environment Variables: Moved all configuration to environment variables

## Tech Debt
* **Token Security:** 
    * Add token blacklisting for logged out tokens
    * Implement token expiration cleanup
    * Add rate limiting for token refresh
* **Code Organization:** Split large files into smaller, focused modules