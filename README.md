# 🎬 Cinema Pro - Ultimate Movie Reservation System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![Stripe](https://img.shields.io/badge/Stripe-008CDD?style=for-the-badge&logo=stripe)](https://stripe.com/)

Cinema Pro is a premium, full-stack movie reservation system featuring a modern web-based GUI, a robust domain-driven FastAPI backend, and seamless Stripe payment integration.

---

## ✨ Key Features
- **Modern Theater UI**: A sleek, dark-themed interface with glassmorphism and smooth animations.
- **Dynamic Seating**: Real-time visualization of seat availability and dynamic selection.
- **Admin Management**: Full control for admins to manage the movie catalog and view bookings.
- **Integrated Payments**: Secure Stripe Checkout flow for processing real-world ticket purchases.
- **Automated Cleanup**: Background logic to release expired reservations after 5 minutes.
- **Domain-Driven Architecture**: Cleanly separated backend logic for better scalability.

---

## 🚀 Quick Start (Docker)

The fastest way to run the entire project is using Docker. This handles the API, Frontend, and Database automatically.

```bash
docker compose up --build
```
- **GUI Access**: `http://localhost:9000`
- **API Documentation**: `http://localhost:8001/docs`

---

## 💻 Manual Setup

### 1. Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Stripe Account](https://stripe.com/) (For Test API keys)

### 2. Database Setup
1. Create the database:
   ```bash
   psql -U postgres -c "CREATE DATABASE movie_reservation;"
   ```
2. Apply the schema and triggers:
   ```bash
   psql -U postgres -d movie_reservation -f schema.sql
   ```

### 3. Environment Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Fill in your credentials:
- `STRIPE_API_KEY`: Your Stripe Secret Key.
- `DB_NAME`, `DB_USER`, `DB_PASS`: Your local Postgres credentials.

### 4. Running the Project
**Backend:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m src.main
```

**Frontend:**
```bash
python3 GUI/app.py
```

---

## 📂 Project Structure
- **`GUI/`**: Frontend application (Static HTML/CSS/JS).
- **`src/`**: Modularized FastAPI backend:
  - `auth/`: User registration, login, and role management.
  - `movies/`: Catalog management and dynamic seat generation.
  - `payments/`: Stripe Checkout and payment verification.
  - `reservations/`: Booking logic and reservation lifecycle.
- **`schema.sql`**: Database structure and PL/pgSQL triggers.
- **`Dockerfile` & `docker-compose.yml`**: Deployment configuration.

---

## 🔐 Credentials
- **Admin**: `admin` / `admin`
- **User**: Register directly through the UI.

---

Enjoy the show! 
