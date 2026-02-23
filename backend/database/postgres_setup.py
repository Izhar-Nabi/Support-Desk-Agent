import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def init_postgres_db(db_url: str):
    from backend.config import settings
    engine = create_engine(settings.POSTGRES_URL)  # Now uses the property
    SessionLocal = sessionmaker(bind=engine)

    # Create tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                city VARCHAR(100)
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tickets (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(id),
                issue TEXT,
                status VARCHAR(50)
            );
        """))
        conn.commit()

    # Insert fake data if empty
    with SessionLocal() as db:
        result = db.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        if result == 0:
            customers = [
                ("Alice Johnson", "New York"),
                ("Bob Smith", "Los Angeles"),
                ("Carol White", "Chicago"),
                ("David Brown", "Houston"),
                ("Eve Davis", "Phoenix")
            ]
            for name, city in customers:
                db.execute(text("INSERT INTO customers (name, city) VALUES (:name, :city)"), {"name": name, "city": city})

            tickets = [
                (1, "Login issue after update", "open"),
                (2, "Billing discrepancy", "resolved"),
                (1, "Can't access dashboard", "in_progress"),
                (3, "Feature request: dark mode", "open"),
                (5, "Payment failed", "resolved")
            ]
            for cid, issue, status in tickets:
                db.execute(text("""
                    INSERT INTO tickets (customer_id, issue, status) 
                    VALUES (:cid, :issue, :status)
                """), {"cid": cid, "issue": issue, "status": status})
            db.commit()

    print("PostgreSQL database initialized with fake data.")