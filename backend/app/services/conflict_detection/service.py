def detect_conflicts(events: list[dict]) -> list[dict]:
    conflicts: list[dict] = []
    ordered = sorted(events, key=lambda item: item["starts_at"])
    for previous, current in zip(ordered, ordered[1:]):
        if previous["ends_at"] > current["starts_at"]:
            conflicts.append({
                "type": "overlap",
                "message": previous["title"] + " overlaps with " + current["title"],
            })
    return conflicts
