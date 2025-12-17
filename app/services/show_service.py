"""
Show service - business logic for showtimes
"""
from app.models.show import Show
from app.models.event import Event
from app.models.auditorium import Auditorium
from app.models.theater import Theater
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import and_


class ShowService:
    """Service for show/showtime operations"""

    @staticmethod
    def get_show_by_id(show_id, event_id):
        """Get show by composite primary key"""
        return Show.query.filter(
            and_(Show.show_id == show_id, Show.event_id == event_id)
        ).first()

    @staticmethod
    def get_shows_for_event(event_id, date=None):
        """Get all shows for an event, optionally filtered by date"""
        query = Show.query.filter(Show.event_id == event_id)

        if date:
            # Filter by date (start and end of day)
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            query = query.filter(
                and_(Show.show_datetime >= start, Show.show_datetime <= end)
            )

        return query.order_by(Show.show_datetime).all()

    @staticmethod
    def get_shows_for_theater(theater_id, date=None):
        """Get all shows for a theater"""
        query = Show.query.join(Auditorium).filter(
            Auditorium.theater_id == theater_id
        )

        if date:
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            query = query.filter(
                and_(Show.show_datetime >= start, Show.show_datetime <= end)
            )

        return query.order_by(Show.show_datetime).all()

    @staticmethod
    def get_shows_for_event_and_theater(event_id, theater_id, date=None):
        """Get shows for a specific event at a specific theater"""
        query = Show.query.join(Auditorium).filter(
            and_(
                Show.event_id == event_id,
                Auditorium.theater_id == theater_id
            )
        )

        if date:
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            query = query.filter(
                and_(Show.show_datetime >= start, Show.show_datetime <= end)
            )

        return query.order_by(Show.show_datetime).all()

    @staticmethod
    def get_shows_with_details(event_id=None, theater_id=None, date=None):
        """Get shows with event, theater, and auditorium details"""
        query = db.session.query(Show, Event, Theater, Auditorium).join(
            Event, Show.event_id == Event.event_id
        ).join(
            Auditorium, Show.auditorium_id == Auditorium.auditorium_id
        ).join(
            Theater, Auditorium.theater_id == Theater.theater_id
        )

        if event_id:
            query = query.filter(Show.event_id == event_id)
        if theater_id:
            query = query.filter(Theater.theater_id == theater_id)
        if date:
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            query = query.filter(
                and_(Show.show_datetime >= start, Show.show_datetime <= end)
            )

        return query.order_by(Show.show_datetime).all()

    @staticmethod
    def get_available_dates_for_event(event_id, days_ahead=7):
        """Get dates that have shows for an event"""
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        shows = Show.query.filter(
            and_(
                Show.event_id == event_id,
                Show.show_datetime >= today,
                Show.show_datetime <= end_date
            )
        ).all()

        dates = set()
        for show in shows:
            dates.add(show.show_datetime.date())

        return sorted(list(dates))
