import psycopg2
from fastapi import APIRouter, HTTPException
from src.database import get_db_connection
from .schemas import AuthRequest, AuthResponse

router = APIRouter(tags=["auth"])

@router.get("/users")
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register", response_model=AuthResponse)
def register(payload: AuthRequest):
    """Register a new regular user in the DB."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, 'user') RETURNING username, role;",
            (payload.username, payload.password)
        )
        user = cur.fetchone()
        conn.commit()
        return AuthResponse(username=user[0], role=user[1])
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Username already exists.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.post("/forgot/password") 
def forgot_password(payload: AuthRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE users SET password = %s WHERE username = %s RETURNING username;",
            ('hadi', payload.username) 
        )
        
        updated_user = cur.fetchone()
        conn.commit()

        if not updated_user:
            raise HTTPException(status_code=404, detail="Username not found.")
            
        return {"message": f"Password for {payload.username} updated successfully."}

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest):
    """Login by checking the users table."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT username, role FROM users WHERE username = %s AND password = %s;",
            (payload.username, payload.password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return AuthResponse(username=user[0], role=user[1])
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
