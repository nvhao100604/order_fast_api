
from sqlalchemy.orm import Session

from app.crud import dashboard as dash_crud

def get_all_orders(db: Session):
    return dash_crud.get_all_orders(db)

def get_all_tables(db: Session):
    return dash_crud.get_all_tables(db)

