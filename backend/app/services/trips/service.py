from app.db.models.trip import Trip


def build_trip(*, owner_id: str, name: str, description: str | None, starts_at, ends_at, visibility: str) -> Trip:
    return Trip(owner_id=owner_id, name=name, description=description, starts_at=starts_at, ends_at=ends_at, visibility=visibility)
