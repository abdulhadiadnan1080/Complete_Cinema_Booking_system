import os
import stripe
from fastapi import APIRouter, HTTPException
from src.database import get_db_connection

router = APIRouter(prefix="/payment", tags=["payments"])

stripe.api_key = os.getenv("STRIPE_API_KEY")
GUI_URL = os.getenv("GUI_URL", "http://localhost:9000")

@router.post("/create-session/{movie_id}/{row}/{num}")
def create_payment_session(movie_id: int, row: str, num: int):
    """Creates a real Stripe Checkout Session for a seat booking."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Get seat price and movie name for Stripe
        cur.execute(
            "SELECT s.price, m.movie_name FROM seats s JOIN movies m ON s.movie_id = m.movie_id "
            "WHERE s.movie_id = %s AND s.row_label = %s AND s.seat_number = %s;",
            (movie_id, row.upper(), num)
        )
        data = cur.fetchone()
        cur.close()
        conn.close()
        
        if not data:
            raise HTTPException(status_code=404, detail="Seat or Movie not found")
        
        price_cents = int(data[0] * 100) # Stripe uses cents
        movie_name = data[1]

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': f"Seat {row}{num} - {movie_name}"},
                    'unit_amount': price_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{GUI_URL}/success?movie_id={movie_id}&row={row}&num={num}",
            cancel_url=f"{GUI_URL}/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm/{movie_id}/{row}/{num}")
def confirm_payment(movie_id: int, row: str, num: int):
    """Finalizes the booking after 'payment'."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # We assume payment is successful, so we clear the timer but keep the seat booked
        # In a real app, we'd mark 'is_paid' = TRUE
        cur.execute(
            "UPDATE seats SET booked_at = NULL WHERE movie_id = %s AND row_label = %s AND seat_number = %s RETURNING seat_id;",
            (movie_id, row.upper(), num)
        )
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not updated:
             raise HTTPException(status_code=404, detail="Reservation not found.")
        return {"message": "Payment confirmed. Your ticket is ready!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
