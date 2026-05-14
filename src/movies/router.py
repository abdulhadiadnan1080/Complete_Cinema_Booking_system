from fastapi import APIRouter, HTTPException
from typing import List
from datetime import timedelta
from src.database import get_db_connection, cleanup_expired_reservations
from .schemas import MovieCreate, MovieResponse, SeatResponse

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=List[MovieResponse])
def list_movies():
    """Returns all movies in the database (with auto-cleanup check)."""
    cleanup_expired_reservations()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT movie_id, movie_name, duration_minutes, start_time, end_time FROM movies ORDER BY movie_id;")
        movies = cur.fetchall()
        cur.close()
        conn.close()
        return [
            MovieResponse(movie_id=m[0], movie_name=m[1], duration_minutes=m[2], start_time=m[3], end_time=m[4])
            for m in movies
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=MovieResponse)
def add_movie(movie: MovieCreate):
    """Adds a new movie. The DB trigger automatically generates 50 seats."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        end_time = movie.start_time + timedelta(minutes=movie.duration_minutes)
        cur.execute(
            "INSERT INTO movies (movie_name, duration_minutes, start_time, end_time) VALUES (%s, %s, %s, %s) RETURNING movie_id;",
            (movie.name, movie.duration_minutes, movie.start_time, end_time)
        )
        movie_id = cur.fetchone()[0]
        conn.commit()
        return MovieResponse(
            movie_id=movie_id,
            movie_name=movie.name,
            duration_minutes=movie.duration_minutes,
            start_time=movie.start_time,
            end_time=end_time
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.delete("/{movie_id}")
def delete_movie(movie_id: int):
    """Deletes a movie and all its seats (via ON DELETE CASCADE)."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM movies WHERE movie_id = %s RETURNING movie_name;", (movie_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not deleted:
            raise HTTPException(status_code=404, detail="Movie not found")
        return {"message": f"Movie '{deleted[0]}' and its seats removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{movie_id}/seats", response_model=List[SeatResponse])
def list_seats(movie_id: int):
    """Returns all seats for a given movie (with auto-cleanup check)."""
    cleanup_expired_reservations()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT seat_id, row_label, seat_number, is_booked, price, booked_at, username FROM seats WHERE movie_id = %s ORDER BY row_label, seat_number;",
            (movie_id,)
        )
        seats = cur.fetchall()
        cur.close()
        conn.close()
        return [
            SeatResponse(
                seat_id=s[0], row_label=s[1], seat_number=s[2], 
                is_booked=s[3], price=float(s[4]), booked_at=s[5], username=s[6]
            )
            for s in seats
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
