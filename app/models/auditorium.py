"""
Auditorium model
"""
from app.extensions import db


class Auditorium(db.Model):
    __tablename__ = 'auditoriums'

    auditorium_id = db.Column(db.String(50), primary_key=True)
    theater_id = db.Column(db.String(50), db.ForeignKey('theaters.theater_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer)

    # Relationships
    theater = db.relationship('Theater', back_populates='auditoriums')
    seats = db.relationship('Seat', back_populates='auditorium', lazy='dynamic')
    shows = db.relationship('Show', back_populates='auditorium', lazy='dynamic')

    def __repr__(self):
        return f'<Auditorium {self.name}>'

    def to_dict(self):
        return {
            'auditorium_id': self.auditorium_id,
            'theater_id': self.theater_id,
            'name': self.name,
            'capacity': self.capacity
        }
