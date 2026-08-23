import os

from verify_flow import Signup, client_from_environment, start_signup


signup = Signup(
    email=os.environ.get("DEMO_TENANT_EMAIL", "tenant@example.com"),
    name="Mina Chen",
    maintenance_request="Leaking kitchen tap",
    tenant_document="lease.pdf",
    inspection_reminder="Annual inspection on 2026-09-15",
)
result = start_signup(signup, "https://example.com/verify/demo", client_from_environment())
print("signup verification queued:", result)
