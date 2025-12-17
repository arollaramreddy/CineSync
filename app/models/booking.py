"""
Booking model
"""
from app.extensions import db


class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.String(50), primary_key=True)
    customer_id = db.Column(db.String(50), db.ForeignKey('customers.customer_id'), nullable=False)
    show_id = db.Column(db.String(50), db.ForeignKey('shows.show_id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    booked_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    customer = db.relationship('Customer', back_populates='bookings')
    show = db.relationship('Show', back_populates='bookings')
    booking_seats = db.relationship('BookingSeat', back_populates='booking', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.booking_id}>'

    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'customer_id': self.customer_id,
            'show_id': self.show_id,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'booked_at': self.booked_at.isoformat() if self.booked_at else None
        }
