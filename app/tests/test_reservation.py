from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.enum import ReservationStatus, TableStatus
from app.models.ordering import Table
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationFilter
from app.services import reservation as reservation_service
from app.crud import table as table_crud

def test_reservation_flow():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        # Create a table
        table = Table(number=1, minCapacity=2, maxCapacity=4, status=TableStatus.EMPTY)
        db.add(table)
        db.commit()
        db.refresh(table)

        # 1. Create Reservation
        res_time = datetime.now(timezone.utc) + timedelta(days=1)
        create_data = ReservationCreate(
            fullName="Nguyen Van A",
            email="nguyenvana@example.com",
            phoneNumber="0987654321",
            numberOfGuests=4,
            reservationTime=res_time,
            specialRequests="Cho bàn gần cửa sổ"
        )

        res = reservation_service.create_reservation_service(db=db, data=create_data, current_user=None)
        assert res.id is not None
        assert res.status == ReservationStatus.PENDING
        assert res.fullName == "Nguyen Van A"
        print("1. Create reservation OK! ID:", res.id)

        # 2. Get Reservations List
        reservations, total = reservation_service.get_reservations_service(
            db=db, filters={}, page=1, limit=10, current_user=None
        )
        assert total == 1
        assert len(reservations) == 1
        print("2. Get reservations OK! Total:", total)

        # 3. Update Reservation (Confirm and assign table)
        update_data = ReservationUpdate(
            status=ReservationStatus.CONFIRMED,
            tableID=table.id
        )
        updated_res = reservation_service.update_reservation_service(
            db=db, reservation_id=res.id, update_data=update_data, current_user=None
        )
        assert updated_res.status == ReservationStatus.CONFIRMED
        assert updated_res.tableID == table.id

        # Verify Table status changed to RESERVED
        refreshed_table = table_crud.get_table(db, table.id)
        assert refreshed_table.status == TableStatus.RESERVED
        print("3. Confirm & Assign table OK! Table Status:", refreshed_table.status)

        # 4. Cancel Reservation
        cancelled_res = reservation_service.cancel_reservation_service(
            db=db, reservation_id=res.id, current_user=None
        )
        assert cancelled_res.status == ReservationStatus.CANCELLED

        # Verify Table status released back to EMPTY
        refreshed_table_after_cancel = table_crud.get_table(db, table.id)
        assert refreshed_table_after_cancel.status == TableStatus.EMPTY
        print("4. Cancel reservation OK! Table Status released to:", refreshed_table_after_cancel.status)

        print("\n🎉 ALL RESERVATION TESTS PASSED SUCCESSFULLY!")

    finally:
        db.close()

if __name__ == "__main__":
    test_reservation_flow()
