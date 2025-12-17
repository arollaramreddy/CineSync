"""
Seat model
"""
from app.extensions import db


class Seat(db.Model):
    __tablename__ = 'seats'

    seat_id = db.Column(db.String(50), primary_key=True)
    auditorium_id = db.Column(db.String(50), db.ForeignKey('auditoriums.auditorium_id'), nullable=False)
    auditorium_name = db.Column(db.String(100))
    seat_no = db.Column(db.String(10), nullable=False)

    # Relationships
    auditorium = db.relationship('Auditorium', back_populates='seats')
    booking_seats = db.relationship('BookingSeat', back_populates='seat', lazy='dynamic')

    def __repr__(self):
        return f'<Seat {self.seat_no}>'

    def to_dict(self):
        return {
            'seat_id': self.seat_id,
            'auditorium_id': self.auditorium_id,
            'auditorium_name': self.auditorium_name,
            'seat_no': self.seat_no
        }
