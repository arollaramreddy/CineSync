"""
Concurrent Booking Service - Handles seat booking with proper concurrency control
Uses SELECT FOR UPDATE to prevent double-booking in CockroachDB
"""
from app.models.booking import Booking
from app.models.booking_seat import BookingSeat
from app.models.show import Show
from app.models.show_seat import ShowSeat
from app.models.seat import Seat
from app.extensions import db
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
import uuid
import os
from datetime import datetime, timedelta


class ConcurrentBookingService:
    """Service for concurrent-safe booking operations"""

    @staticmethod
    def create_booking_with_concurrency_control(customer_id, show_id, seat_ids, session_id=None):
        """
        Create a booking with full concurrency control using SELECT FOR UPDATE

        This prevents race conditions where two users try to book the same seat simultaneously

        Args:
            customer_id: ID of the customer making the booking
            show_id: ID of the show
            seat_ids: List of seat IDs to book
            session_id: Optional session ID for tracking

        Returns:
            Booking object if successful

        Raises:
            ValueError: If seats are unavailable or show not found
            IntegrityError: If concurrent booking conflict occurs
        """

        # Use CockroachDB serializable transaction for strongest consistency
        # This ensures no two transactions can book the same seat

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Start a new transaction
                with db.session.begin_nested():

                    # Step 1: Verify show exists and get price
                    show = Show.query.filter(Show.show_id == show_id).first()
                    if not show:
                        raise ValueError(f"Show {show_id} not found")

                    # Step 2: Lock and check seat availability using SELECT FOR UPDATE
                    # This is the critical section that prevents double-booking
                    show_seats = (
                        ShowSeat.query
                        .filter(
                            and_(
                                ShowSeat.show_id == show_id,
                                ShowSeat.seat_id.in_(seat_ids)
                            )
                        )
                        .with_for_update()  # Row-level lock in CockroachDB
                        .all()
                    )

                    # Verify we got all requested seats
                    if len(show_seats) != len(seat_ids):
                        found_seat_ids = {ss.seat_id for ss in show_seats}
                        missing = set(seat_ids) - found_seat_ids
                        raise ValueError(f"Seats not found for this show: {missing}")

                    # Check if any seat is already booked
                    unavailable_seats = [
                        ss.seat_id for ss in show_seats if not ss.is_available
                    ]
                    if unavailable_seats:
                        raise ValueError(
                            f"Seats already booked: {', '.join(unavailable_seats)}"
                        )

                    # Step 3: Create the booking
                    booking_id = f"BKG-{uuid.uuid4().hex[:8].upper()}"
                    total_amount = show.price * len(seat_ids)

                    booking = Booking(
                        booking_id=booking_id,
                        customer_id=customer_id,
                        show_id=show_id,
                        total_amount=total_amount,
                        booked_at=datetime.now()
                    )
                    db.session.add(booking)

                    # Step 4: Mark seats as unavailable and increment version (optimistic lock)
                    for show_seat in show_seats:
                        show_seat.is_available = False
                        show_seat.booking_id = booking_id
                        show_seat.locked_at = datetime.now()
                        show_seat.locked_by = session_id or customer_id
                        show_seat.version += 1

                    # Step 5: Create booking_seat junction records
                    for seat_id in seat_ids:
                        booking_seat = BookingSeat(
                            id=f"BS-{uuid.uuid4().hex[:8].upper()}",
                            booking_id=booking_id,
                            seat_id=seat_id
                        )
                        db.session.add(booking_seat)

                # Commit the transaction
                db.session.commit()

                return booking

            except IntegrityError as e:
                # Concurrent modification detected, retry
                db.session.rollback()
                retry_count += 1

                if retry_count >= max_retries:
                    raise ValueError(
                        "Booking failed due to high concurrent traffic. Please try again."
                    ) from e

                # Small backoff before retry
                import time
                time.sleep(0.1 * retry_count)

            except Exception as e:
                db.session.rollback()
                raise e

        raise ValueError("Booking failed after maximum retries")

    @staticmethod
    def get_available_seats_for_show(show_id):
        """
        Get all available seats for a show

        Returns:
            List of (Seat, ShowSeat) tuples for available seats
        """
        available = (
            db.session.query(Seat, ShowSeat)
            .join(ShowSeat, Seat.seat_id == ShowSeat.seat_id)
            .filter(
                and_(
                    ShowSeat.show_id == show_id,
                    ShowSeat.is_available == True
                )
            )
            .order_by(Seat.seat_no)
            .all()
        )

        return available

    @staticmethod
    def get_booked_seats_for_show(show_id):
        """Get all booked seats for a show"""
        booked = (
            db.session.query(Seat, ShowSeat)
            .join(ShowSeat, Seat.seat_id == ShowSeat.seat_id)
            .filter(
                and_(
                    ShowSeat.show_id == show_id,
                    ShowSeat.is_available == False
                )
            )
            .order_by(Seat.seat_no)
            .all()
        )

        return booked

    @staticmethod
    def cancel_booking(booking_id):
        """
        Cancel a booking and release seats

        Args:
            booking_id: ID of the booking to cancel

        Returns:
            True if successful
        """
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                raise ValueError(f"Booking {booking_id} not found")

            # Get all show_seats for this booking and release them
            show_seats = ShowSeat.query.filter(
                ShowSeat.booking_id == booking_id
            ).with_for_update().all()

            for show_seat in show_seats:
                show_seat.is_available = True
                show_seat.booking_id = None
                show_seat.locked_at = None
                show_seat.locked_by = None
                show_seat.version += 1

            # Delete booking_seats
            BookingSeat.query.filter(
                BookingSeat.booking_id == booking_id
            ).delete()

            # Delete booking
            db.session.delete(booking)

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def initialize_show_seats(show_id, auditorium_id):
        """
        Initialize show_seats for a new show
        Creates a ShowSeat entry for each seat in the auditorium

        Args:
            show_id: ID of the show
            auditorium_id: ID of the auditorium
        """
        try:
            # Get all seats for the auditorium
            seats = Seat.query.filter(Seat.auditorium_id == auditorium_id).all()

            # Create ShowSeat for each seat
            for seat in seats:
                show_seat = ShowSeat(
                    id=f"SS-{uuid.uuid4().hex[:8].upper()}",
                    show_id=show_id,
                    seat_id=seat.seat_id,
                    is_available=True,
                    version=0
                )
                db.session.add(show_seat)

            db.session.commit()

            return len(seats)

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def cleanup_expired_locks(lock_timeout_minutes=15):
        """
        Clean up any stale locks (seats locked but booking not completed)
        This is a safety mechanism for abandoned bookings

        Args:
            lock_timeout_minutes: Number of minutes after which a lock is considered stale
        """
        try:
            timeout = datetime.now() - timedelta(minutes=lock_timeout_minutes)

            # Find show_seats that are locked but have no booking
            # and were locked more than timeout_minutes ago
            stale_locks = ShowSeat.query.filter(
                and_(
                    ShowSeat.is_available == False,
                    ShowSeat.booking_id == None,
                    ShowSeat.locked_at < timeout
                )
            ).all()

            for show_seat in stale_locks:
                show_seat.is_available = True
                show_seat.locked_at = None
                show_seat.locked_by = None
                show_seat.version += 1

            db.session.commit()

            return len(stale_locks)

        except Exception as e:
            db.session.rollback()
            raise e
