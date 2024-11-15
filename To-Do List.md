# Operative Connect Lite - To-Do List

## Features & Functionality

* **Implement User Roles and Permissions:** Allow different levels of access within organizations (e.g., admin, member). This is crucial for data security and controlling access to sensitive information.
* **Data Validation:** Implement robust input validation for all API endpoints to prevent malicious data and ensure data integrity. This will improve security and reliability.
* **Search Functionality:** Add search capabilities to the organization and partnership lists for easier navigation and management, especially with larger datasets.
* **Partnership Details:** Allow viewing and managing details of a specific partnership, including adding/editing partnership attributes (e.g., status, dates).
* **UI Enhancements:** Develop a more user-friendly and comprehensive UI for interacting with the application. (Consider design, user experience)
* **Testing:** Implement more comprehensive tests (unit, integration) to ensure code quality and prevent regressions. Aim for high test coverage.
* **API Documentation:** Generate and publish comprehensive API documentation (e.g., using Swagger/OpenAPI) to facilitate integration and understanding of the API.
* **Error Handling:** Improve error handling and logging across the application to provide more informative error messages and aid debugging. This includes consistent error responses from the API.
* **Deployment Automation:** Automate the deployment process to Cloud Functions for smoother releases and faster iterations.

## Tech Debt

* **Secret Management:** Evaluate using a more robust secret management solution than storing the JWT secret key directly in Secret Manager. Consider using key rotation as well.
* **Direct BigQuery Access from Cloud Functions:** Refactor the code to avoid direct BigQuery access from Cloud Functions. Implement a service layer or an API for interacting with BigQuery to decouple data access. This improves security and maintainability.
* **Error Responses (All Endpoints):** Standardize error responses across all API endpoints, providing consistent error codes and messages. This improves the developer experience and allows for easier error handling on the client-side.
* **Dependency Management:** Use a `requirements.txt` file to manage dependencies explicitly. This helps ensure consistent environments and simplifies deployment.