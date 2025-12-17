"""
Concurrency Test for CineSync Seat Booking
Demonstrates that CockroachDB with SELECT FOR UPDATE prevents double-booking
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models import Show, ShowSeat, Booking, Customer
from app.services.concurrent_booking_service import ConcurrentBookingService
import threading
import time
from datetime import datetime

# Test configuration
NUM_CONCURRENT_USERS = 5  # Number of users trying to book simultaneously
SAME_SEATS = True  # True = all users try same seats, False = different seats


def attempt_booking(user_num, customer_id, show_id, seat_ids, results, app):
    """
    Simulate a user attempting to book seats

    Args:
        user_num: User identifier for logging
        customer_id: Customer ID
        show_id: Show ID
        seat_ids: List of seat IDs to book
        results: Shared list to store results
        app: Flask app context
    """
    with app.app_context():
        try:
            session_id = f"SESSION-USER{user_num}"

            print(f"[User {user_num}] Attempting to book seats {seat_ids}...")

            # Simulate some network delay
            time.sleep(0.01 * user_num)

            # Attempt booking with concurrency control
            booking = ConcurrentBookingService.create_booking_with_concurrency_control(
                customer_id=customer_id,
                show_id=show_id,
                seat_ids=seat_ids,
                session_id=session_id
            )

            result = {
                'user': user_num,
                'success': True,
                'booking_id': booking.booking_id,
                'seats': seat_ids,
                'timestamp': datetime.now()
            }
            results.append(result)

            print(f"[User {user_num}] SUCCESS! Booking ID: {booking.booking_id}")

        except ValueError as e:
            result = {
                'user': user_num,
                'success': False,
                'error': str(e),
                'seats': seat_ids,
                'timestamp': datetime.now()
            }
            results.append(result)

            print(f"[User {user_num}] FAILED: {str(e)}")

        except Exception as e:
            result = {
                'user': user_num,
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'seats': seat_ids,
                'timestamp': datetime.now()
            }
            results.append(result)

            print(f"[User {user_num}] ERROR: {str(e)}")


def run_concurrency_test():
    """
    Run the concurrency test
    """
    app = create_app()

    with app.app_context():
        print("="*80)
        print("CINESYNC CONCURRENCY TEST")
        print("Testing CockroachDB seat booking resilience")
        print("="*80)

        # Get a show to test with
        show = Show.query.first()
        if not show:
            print("ERROR: No shows found in database. Please run seed_data.py first.")
            return

        print(f"\nTest Configuration:")
        print(f"  Show ID: {show.show_id}")
        print(f"  Event: {show.event.event_name}")
        print(f"  Auditorium: {show.auditorium.name}")
        print(f"  Concurrent Users: {NUM_CONCURRENT_USERS}")
        print(f"  Booking Mode: {'Same seats (conflict expected)' if SAME_SEATS else 'Different seats'}")

        # Get available seats
        available_seats = ConcurrentBookingService.get_available_seats_for_show(show.show_id)

        if len(available_seats) < 2:
            print("ERROR: Not enough available seats for testing")
            return

        # Get customers for testing
        customers = Customer.query.limit(NUM_CONCURRENT_USERS).all()
        if len(customers) < NUM_CONCURRENT_USERS:
            print(f"ERROR: Need at least {NUM_CONCURRENT_USERS} customers in database")
            return

        # Prepare seat selections
        if SAME_SEATS:
            # All users try to book the same seats (should cause conflicts)
            seat_selections = [
                [available_seats[0][0].seat_id, available_seats[1][0].seat_id]
                for _ in range(NUM_CONCURRENT_USERS)
            ]
            print(f"\nAll users will attempt to book: {seat_selections[0]}")
        else:
            # Each user tries to book different seats
            seat_selections = [
                [available_seats[i*2][0].seat_id, available_seats[i*2+1][0].seat_id]
                for i in range(NUM_CONCURRENT_USERS)
            ]
            print(f"\nEach user will attempt different seats")

        print(f"\n" + "-"*80)
        print("Starting concurrent booking attempts...")
        print("-"*80 + "\n")

        # Shared results list
        results = []

        # Create threads for concurrent booking attempts
        threads = []
        for i in range(NUM_CONCURRENT_USERS):
            thread = threading.Thread(
                target=attempt_booking,
                args=(
                    i + 1,
                    customers[i].customer_id,
                    show.show_id,
                    seat_selections[i],
                    results,
                    app
                )
            )
            threads.append(thread)

        # Start all threads simultaneously
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()

        # Analyze results
        print(f"\n" + "="*80)
        print("TEST RESULTS")
        print("="*80)

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        print(f"\nTotal Attempts: {len(results)}")
        print(f"Successful Bookings: {len(successful)}")
        print(f"Failed Bookings: {len(failed)}")
        print(f"Execution Time: {end_time - start_time:.3f} seconds")

        if successful:
            print(f"\nSuccessful Bookings:")
            for r in successful:
                print(f"  User {r['user']}: {r['booking_id']} - Seats: {r['seats']}")

        if failed:
            print(f"\nFailed Bookings (Expected if testing same seats):")
            for r in failed:
                print(f"  User {r['user']}: {r['error']}")

        # Verify database state
        print(f"\n" + "-"*80)
        print("Database Verification:")
        print("-"*80)

        if SAME_SEATS:
            # Check that only ONE booking succeeded for the contested seats
            seat_ids = seat_selections[0]
            show_seats = ShowSeat.query.filter(
                db.and_(
                    ShowSeat.show_id == show.show_id,
                    ShowSeat.seat_id.in_(seat_ids)
                )
            ).all()

            booked_count = sum(1 for ss in show_seats if not ss.is_available)

            print(f"\nContested Seats: {seat_ids}")
            for ss in show_seats:
                print(f"  Seat {ss.seat_id}:")
                print(f"    Available: {ss.is_available}")
                print(f"    Booking ID: {ss.booking_id}")
                print(f"    Version: {ss.version}")

            if booked_count == len(seat_ids) and len(successful) == 1:
                print(f"\n✓ SUCCESS: Concurrency control working correctly!")
                print(f"  - Exactly 1 booking succeeded")
                print(f"  - {len(failed)} bookings correctly failed")
                print(f"  - No double-booking occurred")
            else:
                print(f"\n✗ FAILURE: Concurrency control issue detected!")
                print(f"  - Multiple bookings may have succeeded")

        print("\n" + "="*80)


if __name__ == '__main__':
    run_concurrency_test()
