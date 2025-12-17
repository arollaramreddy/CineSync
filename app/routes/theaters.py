"""
Theater routes - theater listings and details
"""
from flask import Blueprint, render_template, request
from app.services.theater_service import TheaterService
from app.services.show_service import ShowService
from datetime import datetime

theaters_bp = Blueprint('theaters', __name__)


@theaters_bp.route('/')
def list_theaters():
    """List all theaters"""
    city = request.args.get('city')

    if city:
        theaters = TheaterService.get_theaters_by_city(city)
    else:
        theaters = TheaterService.get_all_theaters()

    cities = TheaterService.get_cities()

    return render_template('theaters/list.html',
                          theaters=theaters,
                          cities=cities,
                          selected_city=city)


@theaters_bp.route('/<theater_id>')
def theater_detail(theater_id):
    """Theater detail page"""
    theater = TheaterService.get_theater_by_id(theater_id)

    if not theater:
        return "Theater not found", 404

    # Get auditoriums
    auditoriums = TheaterService.get_theater_auditoriums(theater_id)

    # Get today's shows
    today = datetime.now().date()
    shows_data = ShowService.get_shows_with_details(theater_id=theater_id, date=today)

    return render_template('theaters/detail.html',
                          theater=theater,
                          auditoriums=auditoriums,
                          shows_data=shows_data,
                          today=today)
