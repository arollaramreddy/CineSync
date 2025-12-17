"""
Check database schema and get sample data
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url, pool_pre_ping=True)

with engine.connect() as conn:
    # Get shows schema
    print("SHOWS table schema:")
    print("="*60)
    columns = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'shows'
        ORDER BY ordinal_position
    """)).fetchall()

    for col in columns:
        print(f"{col[0]:<20} {col[1]:<15} {col[2]}")

    print("\n\nSample shows data:")
    print("="*60)
    shows = conn.execute(text("""
        SELECT *
        FROM shows
        LIMIT 5
    """)).fetchall()

    for show in shows:
        print(show)

    print("\n\nSample customer data:")
    print("="*60)
    customers = conn.execute(text("""
        SELECT customer_id
        FROM customers
        LIMIT 5
    """)).fetchall()

    for cust in customers:
        print(cust[0])

    print("\n\nSample seat data:")
    print("="*60)
    seats = conn.execute(text("""
        SELECT seat_id
        FROM seats
        LIMIT 5
    """)).fetchall()

    for seat in seats:
        print(seat[0])
