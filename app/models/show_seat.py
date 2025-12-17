"""
ShowSeat model - tracks seat availability for each show
This is crucial for concurrency control in seat booking
"""
from app.extensions import db
from sqlalchemy import UniqueConstraint


class ShowSeat(db.Model):
    __tablename__ = 'show_seats'
    __table_args__ = (
        UniqueConstraint('show_id', 'seat_id', name='unique_show_seat'),
    )

    id = db.Column(db.String(50), primary_key=True)
    show_id = db.Column(db.String(50), db.ForeignKey('shows.show_id'), nullable=False, index=True)
    seat_id = db.Column(db.String(50), db.ForeignKey('seats.seat_id'), nullable=False, index=True)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    booking_id = db.Column(db.String(50), db.ForeignKey('bookings.booking_id'), nullable=True)
    locked_at = db.Column(db.DateTime, nullable=True)
    locked_by = db.Column(db.String(100), nullable=True)  # Session/transaction ID
    version = db.Column(db.Integer, default=0, nullable=False)  # For optimistic locking

    # Relationships
    show = db.relationship('Show', backref='show_seats')
    seat = db.relationship('Seat', backref='show_seats')
    booking = db.relationship('Booking', backref='show_seat_locks')

    def __repr__(self):
        return f'<ShowSeat {self.show_id}:{self.seat_id} available={self.is_available}>'

    def to_dict(self):
        return {
            'id': self.id,
            'show_id': self.show_id,
            'seat_id': self.seat_id,
            'is_available': self.is_available,
            'booking_id': self.booking_id,
            'version': self.version
        }
