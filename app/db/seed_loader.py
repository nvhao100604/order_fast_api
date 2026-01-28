import re
from pathlib import Path
from typing import List, Dict

from app.models import Category, Dish

# =========================
# PATH
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]
SQL_DIR = BASE_DIR / "sql" / "mysql"


# =========================
# REGEX: INSERT INTO table (cols...) VALUES (...)
# =========================
INSERT_RE = re.compile(
    r"""
    INSERT\s+INTO\s+`?(\w+)`?\s*
    \(([^)]+)\)\s*
    VALUES\s*(.*?)
    (?=;|\Z)
    """,
    re.I | re.S | re.X,
)


# =========================
# PARSE VALUES BLOCK
# =========================
def _parse_insert_values(values_block: str) -> List[List[str]]:
    """
    Input:
        (1,'A'),(2,'B')
    Output:
        [['1','A'], ['2','B']]
    """
    rows: List[List[str]] = []

    for row in re.findall(r"\((.*?)\)", values_block, re.S):
        cols = []
        current = ""
        in_string = False

        for ch in row:
            if ch == "'" and not in_string:
                in_string = True
                continue
            elif ch == "'" and in_string:
                in_string = False
                continue

            if ch == "," and not in_string:
                cols.append(current.strip())
                current = ""
            else:
                current += ch

        if current:
            cols.append(current.strip())

        rows.append(cols)

    return rows


def _rows_to_dicts(columns: str, rows: List[List[str]]) -> List[Dict[str, str]]:
    col_names = [c.strip().strip("`") for c in columns.split(",")]
    return [dict(zip(col_names, r)) for r in rows]


# =========================
# LOAD CATEGORIES
# =========================
def load_categories_from_sql(filename: str) -> List[Category]:
    sql = (SQL_DIR / filename).read_text(encoding="utf-8")
    categories: List[Category] = []

    for match in INSERT_RE.finditer(sql):
        if match.group(1) != "categories":
            continue

        columns = match.group(2)
        rows = _parse_insert_values(match.group(3))
        records = _rows_to_dicts(columns, rows)

        for r in records:
            categories.append(
                Category(
                    id=int(r["id"]),
                    name=r["name"],
                )
            )

    return categories


# =========================
# LOAD DISHES
# =========================
def load_dishes_from_sql(filename: str) -> List[Dish]:
    sql = (SQL_DIR / filename).read_text(encoding="utf-8")
    dishes: List[Dish] = []

    for match in INSERT_RE.finditer(sql):
        if match.group(1) != "dish":
            continue

        columns = match.group(2)
        rows = _parse_insert_values(match.group(3))
        records = _rows_to_dicts(columns, rows)

        for r in records:
            dishes.append(
                Dish(
                    id=int(r["id"]),
                    name=r["name"],
                    price=float(r["price"]),
                    imgUrl=r["imgUrl"],
                    describe=r["describe"],
                    status=int(r["status"]),
                    categoryID=int(r["categoryID"]),
                )
            )

    return dishes
