"""
Booking service - business logic for bookings
"""
from app.models.booking import Booking
from app.models.booking_seat import BookingSeat
from app.models.show import Show
from app.extensions import db
from app.services.seat_service import SeatService
import uuid
from datetime import datetime


class BookingService:
    """Service for booking operations"""

    @staticmethod
    def create_booking(customer_id, show_id, event_id, seat_ids):
        """
        Create a new booking with seats
        Uses transaction to ensure atomicity
        """
        try:
            # Get show to calculate price
            show = Show.query.filter(
                db.and_(Show.show_id == show_id, Show.event_id == event_id)
            ).first()

            if not show:
                raise ValueError("Show not found")

            # Verify seats are available
            if not SeatService.are_seats_available(seat_ids, show_id):
                raise ValueError("One or more seats are not available")

            # Calculate total amount
            num_seats = len(seat_ids)
            total_amount = show.price * num_seats

            # Create booking
            booking_id = f"BKG-{uuid.uuid4().hex[:8].upper()}"
            booking = Booking(
                booking_id=booking_id,
                customer_id=customer_id,
                show_id=show_id,
                total_amount=total_amount,
                booked_at=datetime.now()
            )

            db.session.add(booking)

            # Create booking_seats entries
            for seat_id in seat_ids:
                booking_seat = BookingSeat(
                    id=f"BS-{uuid.uuid4().hex[:8].upper()}",
                    booking_id=booking_id,
                    seat_id=seat_id
                )
                db.session.add(booking_seat)

            db.session.commit()

            return booking

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_booking_by_id(booking_id):
        """Get booking by ID"""
        return Booking.query.get(booking_id)

    @staticmethod
    def get_customer_bookings(customer_id):
        """Get all bookings for a customer"""
        return Booking.query.filter(
            Booking.customer_id == customer_id
        ).order_by(Booking.booked_at.desc()).all()

    @staticmethod
    def get_booking_details(booking_id):
        """Get booking with all related information"""
        booking = Booking.query.get(booking_id)
        if not booking:
            return None

        # Get seats
        booking_seats = BookingSeat.query.filter(
            BookingSeat.booking_id == booking_id
        ).all()

        seats = [bs.seat for bs in booking_seats]

        return {
            'booking': booking,
            'seats': seats,
            'num_seats': len(seats)
        }

    @staticmethod
    def cancel_booking(booking_id):
        """
        Cancel a booking (delete booking and booking_seats)
        Note: This is a simple implementation. In production, you might want soft deletes
        """
        try:
            # Delete booking_seats first (foreign key constraint)
            BookingSeat.query.filter(
                BookingSeat.booking_id == booking_id
            ).delete()

            # Delete booking
            Booking.query.filter(Booking.booking_id == booking_id).delete()

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_booking_with_show_details(booking_id):
        """Get booking with show and event details"""
        booking = Booking.query.get(booking_id)
        if not booking:
            return None

        # Get show details
        show = Show.query.filter(Show.show_id == booking.show_id).first()

        # Get seats
        booking_seats = BookingSeat.query.filter(
            BookingSeat.booking_id == booking_id
        ).all()
        seats = [bs.seat for bs in booking_seats]

        return {
            'booking': booking,
            'show': show,
            'event': show.event if show else None,
            'auditorium': show.auditorium if show else None,
            'theater': show.auditorium.theater if show and show.auditorium else None,
            'seats': seats
        }
