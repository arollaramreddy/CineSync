"""
Show routes - showtimes and selection
"""
from flask import Blueprint, render_template, request
from app.services.show_service import ShowService
from app.services.event_service import EventService
from app.services.theater_service import TheaterService
from datetime import datetime

shows_bp = Blueprint('shows', __name__)


@shows_bp.route('/select')
def select_show():
    """Show selection page for event and theater"""
    event_id = request.args.get('event_id')
    theater_id = request.args.get('theater_id')
    date_str = request.args.get('date')

    if not event_id:
        return "Event ID required", 400

    event = EventService.get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    # Parse date
    show_date = None
    if date_str:
        try:
            show_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            show_date = datetime.now().date()
    else:
        show_date = datetime.now().date()

    # Get shows
    if theater_id:
        theater = TheaterService.get_theater_by_id(theater_id)
        shows_data = ShowService.get_shows_with_details(
            event_id=event_id,
            theater_id=theater_id,
            date=show_date
        )
    else:
        theater = None
        shows_data = ShowService.get_shows_with_details(
            event_id=event_id,
            date=show_date
        )

    # Group shows by theater
    theaters_shows = {}
    for show, event_obj, theater_obj, auditorium in shows_data:
        if theater_obj.theater_id not in theaters_shows:
            theaters_shows[theater_obj.theater_id] = {
                'theater': theater_obj,
                'shows': []
            }
        theaters_shows[theater_obj.theater_id]['shows'].append({
            'show': show,
            'auditorium': auditorium
        })

    return render_template('shows/select.html',
                          event=event,
                          theater=theater,
                          show_date=show_date,
                          theaters_shows=theaters_shows)
