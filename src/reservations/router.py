from fastapi import APIRouter, HTTPException, Body
from datetime import datetime
from src.database import get_db_connection, cleanup_expired_reservations

router = APIRouter(prefix="/reserve", tags=["reservations"])

@router.post("/{movie_id}/{row_label}/{seat_number}")
def reserve_seat(movie_id: int, row_label: str, seat_number: int, username: str = Body(..., embed=True)):
    """Books a specific seat for a movie. Starts the 5-minute timer."""
    cleanup_expired_reservations()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        now = datetime.now()
        cur.execute(
            "UPDATE seats SET is_booked = TRUE, booked_at = %s, username = %s "
            "WHERE movie_id = %s AND row_label = %s AND seat_number = %s AND is_booked = FALSE "
            "RETURNING seat_id;",
            (now, username, movie_id, row_label.upper(), seat_number)
        )
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            raise HTTPException(status_code=400, detail="Seat not available or already booked")
        return {"message": "Seat held for 5 minutes. Please complete payment.", "booked_at": now}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.delete("/{movie_id}/{row_label}/{seat_number}")
def cancel_reservation(movie_id: int, row_label: str, seat_number: int, username: str = Body(..., embed=True), role: str = Body(..., embed=True)):
    """Cancels a booking. Admin can cancel any, Users can only cancel their own."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check ownership unless admin
        if role != "admin":
            cur.execute(
                "SELECT username FROM seats WHERE movie_id = %s AND row_label = %s AND seat_number = %s;",
                (movie_id, row_label.upper(), seat_number)
            )
            owner = cur.fetchone()
            if not owner or owner[0] != username:
                raise HTTPException(status_code=403, detail="You can only cancel your own bookings.")

        cur.execute(
            "UPDATE seats SET is_booked = FALSE, booked_at = NULL, username = NULL "
            "WHERE movie_id = %s AND row_label = %s AND seat_number = %s RETURNING seat_id;",
            (movie_id, row_label.upper(), seat_number)
        )
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            raise HTTPException(status_code=404, detail="Booking not found.")
        return {"message": "Reservation cancelled successfully."}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
