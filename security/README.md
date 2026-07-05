# Security — JWT Authentication Middleware (Future)
#
# This directory will contain authentication and authorization utilities
# for the Gestia Spring Boot REST API integration.
#
# Planned contents:
#
#   jwt_validator.py
#     - Validate incoming JWT tokens issued by Gestia Spring Security
#     - Extract business_id and user claims from the token payload
#     - Inject claims into the ADK session context
#
#   auth_middleware.py
#     - FastAPI middleware to authenticate requests before they reach the agent
#     - Reject unauthenticated or unauthorized requests with HTTP 401/403
#
# Integration notes:
#   - Gestia uses Spring Security with JWT (HS256 or RS256 — confirm with backend team)
#   - The validated business_id from JWT claims replaces get_demo_business_context()
#     in app/app_utils/context.py
#   - JWT secrets must be loaded from environment variables, never hardcoded
