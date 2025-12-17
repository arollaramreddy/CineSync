"""
Show model
"""
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID


class Show(db.Model):
    __tablename__ = 'shows'

    show_id = db.Column(db.String(50), primary_key=True)
    event_id = db.Column(UUID(as_uuid=True), db.ForeignKey('events.event_id'), nullable=False)
    auditorium_id = db.Column(db.String(50), db.ForeignKey('auditoriums.auditorium_id'), nullable=False)
    show_datetime = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    event = db.relationship('Event', back_populates='shows')
    auditorium = db.relationship('Auditorium', back_populates='shows')
    bookings = db.relationship('Booking', back_populates='show', lazy='dynamic')

    def __repr__(self):
        return f'<Show {self.show_id}>'

    def to_dict(self):
        return {
            'show_id': self.show_id,
            'event_id': str(self.event_id),
            'auditorium_id': self.auditorium_id,
            'show_datetime': self.show_datetime.isoformat() if self.show_datetime else None,
            'price': float(self.price) if self.price else 0
        }
