---
globs:
  - "backend/routers/**/*.py"
  - "backend/main.py"
---

- Every endpoint must declare `response_model` and `status_code` explicitly
- Use `HTTPException(status_code=404)` for missing resources, never return None
- 201 for POST (creation), 204 for DELETE (no body), 200 for GET/PUT
- Query params with `Query(...)` for required, `Query(None)` for optional
- After adding or modifying any endpoint, note that openapi.yaml should be regenerated
- CORS is configured in main.py — do not add it per-router
