-- Cinema Pro Database Schema
-- Run these commands in your PostgreSQL database (movie_reservation)

-- 1. Create Tables
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS movies (
    movie_id SERIAL PRIMARY KEY,
    movie_name VARCHAR(255) NOT NULL,
    duration_minutes INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS seats (
    seat_id SERIAL PRIMARY KEY,
    movie_id INTEGER REFERENCES movies(movie_id) ON DELETE CASCADE,
    row_label CHAR(1) NOT NULL CHECK (row_label IN ('A', 'B', 'C', 'D', 'E')),
    seat_number INTEGER NOT NULL CHECK (seat_number >= 1 AND seat_number <= 10),
    is_booked BOOLEAN DEFAULT FALSE,
    price NUMERIC(6,2) NOT NULL,
    booked_at TIMESTAMP,
    username VARCHAR(100),
    UNIQUE(movie_id, row_label, seat_number)
);

-- 2. Create Trigger Function for Automatic Seat Generation
CREATE OR REPLACE FUNCTION generate_movie_seats()
RETURNS TRIGGER AS $$
DECLARE
    rows CHAR[] := ARRAY['A','B','C','D','E'];
    r CHAR;
    seat_num INT;
    base_price DECIMAL(6,2) := 10.00;
    premium_price DECIMAL(6,2) := 15.00;
BEGIN
    FOREACH r IN ARRAY rows LOOP
        FOR seat_num IN 1..10 LOOP
            INSERT INTO seats (movie_id, row_label, seat_number, price)
            VALUES (
                NEW.movie_id,
                r,
                seat_num,
                CASE 
                    WHEN r IN ('A', 'E') THEN premium_price
                    ELSE base_price
                END
            );
        END LOOP;
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Attach Trigger to Movies Table
DROP TRIGGER IF EXISTS trigger_generate_seats ON movies;
CREATE TRIGGER trigger_generate_seats
AFTER INSERT ON movies
FOR EACH ROW
EXECUTE FUNCTION generate_movie_seats();

-- 4. Insert Default Admin (Optional)
-- Password here is 'admin' (you should change this in production)
INSERT INTO users (username, password, role) 
VALUES ('admin', 'admin', 'admin') 
ON CONFLICT (username) DO NOTHING;
