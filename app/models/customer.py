"""
Customer model
"""
from app.extensions import db


class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Relationships
    bookings = db.relationship('Booking', back_populates='customer', lazy='dynamic')

    def __repr__(self):
        return f'<Customer {self.name}>'

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
