"""
Theater service - business logic for theaters
"""
from app.models.theater import Theater
from app.models.auditorium import Auditorium
from app.extensions import db


class TheaterService:
    """Service for theater operations"""

    @staticmethod
    def get_all_theaters():
        """Get all theaters"""
        return Theater.query.order_by(Theater.name).all()

    @staticmethod
    def get_theater_by_id(theater_id):
        """Get theater by ID"""
        return Theater.query.get(theater_id)

    @staticmethod
    def get_theaters_by_city(city):
        """Get theaters in a specific city"""
        return Theater.query.filter(Theater.city == city).order_by(Theater.name).all()

    @staticmethod
    def get_cities():
        """Get unique cities"""
        result = db.session.query(Theater.city).distinct().filter(
            Theater.city.isnot(None)
        ).order_by(Theater.city).all()
        return [r[0] for r in result]

    @staticmethod
    def get_theater_auditoriums(theater_id):
        """Get all auditoriums for a theater"""
        return Auditorium.query.filter(
            Auditorium.theater_id == theater_id
        ).order_by(Auditorium.name).all()

    @staticmethod
    def search_theaters(search_term):
        """Search theaters by name or city"""
        return Theater.query.filter(
            db.or_(
                Theater.name.ilike(f'%{search_term}%'),
                Theater.city.ilike(f'%{search_term}%')
            )
        ).order_by(Theater.name).all()

    @staticmethod
    def get_nearby_theaters(latitude, longitude, radius_km=10):
        """
        Get theaters near a location
        Note: This requires PostGIS functions for proper implementation
        For now, returns all theaters
        """
        # TODO: Implement proper geography-based search
        # Example SQL: ST_DWithin(geog, ST_MakePoint(lng, lat)::geography, radius_meters)
        return Theater.query.all()
