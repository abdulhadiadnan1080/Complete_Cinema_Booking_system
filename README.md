# 🎬 Cinema Pro - Ultimate Movie Reservation System

Cinema Pro is a premium, full-stack movie reservation system featuring a modern web-based GUI, a robust FastAPI backend, and seamless Stripe payment integration.

---

## ✨ Key Features
- **Modern UI**: A sleek, dark-themed theater interface with glassmorphism and smooth animations.
- **Real-time Seating**: Visualize seat availability and select seats dynamically.
- **Admin Dashboard**: Full control for admins to add/delete movies and manage the catalog.
- **Secure Payments**: Integrated Stripe Checkout for real-world payment processing.
- **Auto-Cleanup**: Automated system to release expired reservations after 5 minutes.
- **Email Notifications**: Ready for Resend integration to send booking confirmations.

---

## 🛠️ Tech Stack
- **Frontend**: HTML5, Vanilla CSS (Modern Aesthetics), Javascript.
- **Backend**: FastAPI (Python), Uvicorn.
- **Database**: PostgreSQL (with Triggers for auto-seat generation).
- **Payments**: Stripe API.

---

## 🚀 Quick Start (Docker)

The fastest way to run the entire project (Database, API, and GUI) is using Docker. You don't even need Python installed!

```bash
docker compose up --build
```
*The database will automatically initialize. Access the GUI at `http://localhost:9000`.*

---

## 💻 Manual Setup

If you prefer to run it manually without Docker, follow these steps:

### 1. Prerequisites
Ensure you have the following installed:
- [Python 3.10+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Stripe Account](https://stripe.com/) (For API keys)

### 2. Database Initialization
1. Create the database:
   ```bash
   psql -U postgres -c "CREATE DATABASE movie_reservation;"
   ```
2. Apply the schema and triggers:
   ```bash
   psql -U postgres -d movie_reservation -f schema.sql
   ```

### 3. Environment Setup
1. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
2. Fill in your credentials:
   ```env
   STRIPE_API_KEY=your_stripe_secret_key
   DB_NAME=movie_reservation
   DB_USER=postgres
   DB_PASS=your_db_password
   GUI_URL=http://localhost:9000
   ```

### 4. Backend Setup
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the API server:
   ```bash
   python3 -m src.main
   ```
   *The API will run at `http://localhost:8001`*

### 5. Frontend Setup
1. In a new terminal, run the GUI server:
   ```bash
   python3 GUI/app.py
   ```
   *The application will open automatically at `http://localhost:9000`*

---

## 🔐 Default Credentials
- **Admin Access**: 
  - Username: `admin`
  - Password: `admin`
- **User Access**: Register a new account directly through the login screen.

---

## 📂 Project Structure
- `GUI/`: Web-based theater interface.
- `workings/`: FastAPI backend and API logic.
- `logic/`: Core Python business logic and models.
- `schema.sql`: Database table definitions and triggers.
- `requirements.txt`: Python dependencies.

---

## 🛠 Troubleshooting
- **Database Error**: Ensure PostgreSQL is running and the credentials in `.env` are correct.
- **Port 8001/9000 occupied**: If the ports are in use, check for existing Python processes and terminate them.
- **Stripe Session Error**: Verify your `STRIPE_API_KEY` is a valid secret key from your Stripe dashboard.

---

Enjoy the movie! 🍿
