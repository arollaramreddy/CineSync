"""
Theater model
"""
from app.extensions import db


class Theater(db.Model):
    __tablename__ = 'theaters'

    theater_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Relationships
    auditoriums = db.relationship('Auditorium', back_populates='theater', lazy='dynamic')

    def __repr__(self):
        return f'<Theater {self.name}>'

    def to_dict(self):
        return {
            'theater_id': self.theater_id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
