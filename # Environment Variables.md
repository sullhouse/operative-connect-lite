# Environment Variables

This document lists and describes all the environment variables used across the API modules, including their default values.

## Environment Variables

### ALLOWED_ORIGINS
- **Description:** A comma-separated list of allowed origins for CORS.
- **Default:** `http://ocl.sullhouse.com,http://localhost:5000,http://127.0.0.1:5000`
- **Usage:** Configures the allowed origins for CORS in the Flask application.

### SECRET_KEY
- **Description:** The secret key used for JWT token encoding and decoding.
- **Default:** `default_secret_key`
- **Usage:** Configures the secret key for the Flask application.

### GCP_PROJECT
- **Description:** The Google Cloud Project ID.
- **Default:** None (must be set)
- **Usage:** Specifies the Google Cloud Project ID for accessing Google Cloud services.

### RATE_LIMITS
- **Description:** The default rate limits for the Flask application.
- **Default:** `200 per day,50 per hour`
- **Usage:** Configures the rate limits for the Flask application.

### REFRESH_RATE_LIMIT
- **Description:** The rate limit for the token refresh endpoint.
- **Default:** `5 per minute`
- **Usage:** Configures the rate limit for the token refresh endpoint.

### FLASK_DEBUG
- **Description:** Enables or disables debug mode in the Flask application.
- **Default:** `False`
- **Usage:** Configures the debug mode for the Flask application.

## Example Usage

To set these environment variables, you can use a `.env` file or set them directly in your deployment environment.

### Using a `.env` File

Create a `.env` file in the root of your project and add the following lines:

```plaintext
ALLOWED_ORIGINS=http://ocl.sullhouse.com,http://localhost:5000,http://127.0.0.1:5000
SECRET_KEY=your_secret_key
GCP_PROJECT=your_gcp_project_id
RATE_LIMITS=200 per day,50 per hour
REFRESH_RATE_LIMIT=5 per minute
FLASK_DEBUG=True