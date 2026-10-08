# app/services/table_recommendation.py
from itertools import combinations
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.ordering import Table
from app.models.enum import TableStatus
from app.services.display_status import compute_display_status


def recommend_tables(
    db: Session,
    guest_count: int,
    area_id: Optional[int] = None
) -> List[Table]:
    """
    Recommend best table(s) for a given guest count.
    
    Strategy:
    1. Filter available/empty tables in specified area (or all areas).
    2. Try to find a single table where maxCapacity >= guest_count.
       Sort by seats ASC (tightest fit first).
    3. If no single table fits, search combinations of 2 to 4 empty tables
       whose combined seats >= guest_count.
       Sort combinations by total capacity ASC, then count ASC.
    4. Return list of recommended Table models.
    """
    if guest_count <= 0:
        return []

    query = db.query(Table).filter(Table.status != TableStatus.DELETED)
    if area_id is not None:
        query = query.filter(Table.areaID == area_id)

    all_tables = query.all()
    # Filter empty tables (checking displayStatus)
    empty_tables = [
        t for t in all_tables
        if compute_display_status(db, t.id) == "EMPTY"
    ]

    # 1. Single table search
    single_fits = [
        t for t in empty_tables
        if t.maxCapacity >= guest_count
    ]
    if single_fits:
        # Pick tightest fit (smallest seats >= guest_count)
        single_fits.sort(key=lambda t: (t.seats, t.maxCapacity))
        return [single_fits[0]]

    # 2. Combination search (2 to 4 tables)
    best_combo = None
    best_capacity = float("inf")

    for k in range(2, min(5, len(empty_tables) + 1)):
        for combo in combinations(empty_tables, k):
            total_seats = sum(t.seats for t in combo)
            if total_seats >= guest_count and total_seats < best_capacity:
                best_capacity = total_seats
                best_combo = list(combo)

    return best_combo or []
