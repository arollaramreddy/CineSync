"""
Event/Movie model
"""
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Event(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_name = db.Column(db.String(255), nullable=False)
    event_type = db.Column(db.String(50))
    language = db.Column(db.String(50))
    duration_mins = db.Column(db.Integer)
    rating = db.Column(db.String(10))

    # Relationships
    shows = db.relationship('Show', back_populates='event', lazy='dynamic')

    def __repr__(self):
        return f'<Event {self.event_name}>'

    def to_dict(self):
        return {
            'event_id': str(self.event_id),
            'event_name': self.event_name,
            'event_type': self.event_type,
            'language': self.language,
            'duration_mins': self.duration_mins,
            'rating': self.rating
        }
