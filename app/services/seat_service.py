"""
Seat service - business logic for seat management
"""
from app.models.seat import Seat
from app.models.booking_seat import BookingSeat
from app.models.booking import Booking
from app.extensions import db
from sqlalchemy import and_


class SeatService:
    """Service for seat operations"""

    @staticmethod
    def get_seats_for_auditorium(auditorium_id):
        """Get all seats in an auditorium"""
        return Seat.query.filter(
            Seat.auditorium_id == auditorium_id
        ).order_by(Seat.seat_no).all()

    @staticmethod
    def get_available_seats_for_show(show_id, auditorium_id):
        """
        Get available seats for a show
        Returns seats that are not booked for this show
        """
        # Get all seats in the auditorium
        all_seats = Seat.query.filter(
            Seat.auditorium_id == auditorium_id
        ).all()

        # Get booked seats for this show
        booked_seat_ids = db.session.query(BookingSeat.seat_id).join(
            Booking, BookingSeat.booking_id == Booking.booking_id
        ).filter(
            Booking.show_id == show_id
        ).all()

        booked_ids = [seat_id[0] for seat_id in booked_seat_ids]

        # Filter out booked seats
        available_seats = [seat for seat in all_seats if seat.seat_id not in booked_ids]

        return available_seats

    @staticmethod
    def get_booked_seats_for_show(show_id):
        """Get seats that are already booked for a show"""
        booked_seats = db.session.query(Seat).join(
            BookingSeat, Seat.seat_id == BookingSeat.seat_id
        ).join(
            Booking, BookingSeat.booking_id == Booking.booking_id
        ).filter(
            Booking.show_id == show_id
        ).all()

        return booked_seats

    @staticmethod
    def get_seat_by_id(seat_id):
        """Get seat by ID"""
        return Seat.query.get(seat_id)

    @staticmethod
    def get_seats_by_ids(seat_ids):
        """Get multiple seats by their IDs"""
        return Seat.query.filter(Seat.seat_id.in_(seat_ids)).all()

    @staticmethod
    def is_seat_available(seat_id, show_id):
        """Check if a specific seat is available for a show"""
        booked = db.session.query(BookingSeat).join(
            Booking, BookingSeat.booking_id == Booking.booking_id
        ).filter(
            and_(
                BookingSeat.seat_id == seat_id,
                Booking.show_id == show_id
            )
        ).first()

        return booked is None

    @staticmethod
    def are_seats_available(seat_ids, show_id):
        """Check if multiple seats are available for a show"""
        for seat_id in seat_ids:
            if not SeatService.is_seat_available(seat_id, show_id):
                return False
        return True

    @staticmethod
    def get_all_seats_with_status(show_id, auditorium_id):
        """
        Get all seats for an auditorium with their booking status
        Returns a list of dicts with seat info and is_booked status
        """
        # Get all seats in the auditorium
        all_seats = Seat.query.filter(
            Seat.auditorium_id == auditorium_id
        ).order_by(Seat.seat_no).all()

        # Get booked seat IDs for this show
        booked_seat_ids = db.session.query(BookingSeat.seat_id).join(
            Booking, BookingSeat.booking_id == Booking.booking_id
        ).filter(
            Booking.show_id == show_id
        ).all()

        booked_ids = {seat_id[0] for seat_id in booked_seat_ids}

        # Create seat list with status
        seats_with_status = []
        for seat in all_seats:
            seats_with_status.append({
                'seat': seat,
                'is_booked': seat.seat_id in booked_ids
            })

        return seats_with_status
