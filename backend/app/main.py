from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, trips, destinations, events, expenses, invitations, integrations, maps, calendar
from app.core.config import settings

app = FastAPI(title="Trips Planner API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/routes/auth", tags=["auth"])
app.include_router(trips.router, prefix="/api/routes/trips", tags=["trips"])
app.include_router(destinations.router, prefix="/api/routes/destinations", tags=["destinations"])
app.include_router(events.router, prefix="/api/routes/events", tags=["events"])
app.include_router(expenses.router, prefix="/api/routes/expenses", tags=["expenses"])
app.include_router(invitations.router, prefix="/api/routes/invitations", tags=["invitations"])
app.include_router(integrations.router, prefix="/api/routes/integrations", tags=["integrations"])
app.include_router(maps.router, prefix="/api/routes/maps", tags=["maps"])
app.include_router(calendar.router, prefix="/api/routes/calendar", tags=["calendar"])
