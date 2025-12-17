"""
Event service - business logic for events/movies
"""
from app.models.event import Event
from app.extensions import db
from sqlalchemy import or_


class EventService:
    """Service for event/movie operations"""

    @staticmethod
    def get_all_events(limit=None):
        """Get all events"""
        query = Event.query
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_event_by_id(event_id):
        """Get event by ID"""
        return Event.query.get(event_id)

    @staticmethod
    def search_events(search_term):
        """Search events by name"""
        return Event.query.filter(
            Event.event_name.ilike(f'%{search_term}%')
        ).all()

    @staticmethod
    def filter_events(event_type=None, language=None, rating=None):
        """Filter events by type, language, or rating"""
        query = Event.query

        if event_type:
            query = query.filter(Event.event_type == event_type)
        if language:
            query = query.filter(Event.language == language)
        if rating:
            query = query.filter(Event.rating == rating)

        return query.all()

    @staticmethod
    def get_featured_events(limit=6):
        """Get featured events for homepage"""
        return Event.query.limit(limit).all()

    @staticmethod
    def get_event_types():
        """Get unique event types"""
        result = db.session.query(Event.event_type).distinct().filter(
            Event.event_type.isnot(None)
        ).all()
        return [r[0] for r in result]

    @staticmethod
    def get_languages():
        """Get unique languages"""
        result = db.session.query(Event.language).distinct().filter(
            Event.language.isnot(None)
        ).all()
        return [r[0] for r in result]

    @staticmethod
    def get_ratings():
        """Get unique ratings"""
        result = db.session.query(Event.rating).distinct().filter(
            Event.rating.isnot(None)
        ).all()
        return [r[0] for r in result]
