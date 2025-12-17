"""
BookingSeat model - junction table
"""
from app.extensions import db


class BookingSeat(db.Model):
    __tablename__ = 'booking_seats'

    id = db.Column(db.String(50), primary_key=True)
    booking_id = db.Column(db.String(50), db.ForeignKey('bookings.booking_id'), nullable=False)
    seat_id = db.Column(db.String(50), db.ForeignKey('seats.seat_id'), nullable=False)

    # Relationships
    booking = db.relationship('Booking', back_populates='booking_seats')
    seat = db.relationship('Seat', back_populates='booking_seats')

    def __repr__(self):
        return f'<BookingSeat {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'seat_id': self.seat_id
        }
