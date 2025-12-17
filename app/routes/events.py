"""
Event routes - event/movie listings and details
"""
from flask import Blueprint, render_template, request
from app.services.event_service import EventService
from app.services.show_service import ShowService
from app.services.theater_service import TheaterService

events_bp = Blueprint('events', __name__)


@events_bp.route('/')
def list_events():
    """List all events with optional filters"""
    event_type = request.args.get('type')
    language = request.args.get('language')
    rating = request.args.get('rating')

    if event_type or language or rating:
        events = EventService.filter_events(event_type, language, rating)
    else:
        events = EventService.get_all_events()

    # Get filter options
    event_types = EventService.get_event_types()
    languages = EventService.get_languages()
    ratings = EventService.get_ratings()

    return render_template('events/list.html',
                          events=events,
                          event_types=event_types,
                          languages=languages,
                          ratings=ratings,
                          selected_type=event_type,
                          selected_language=language,
                          selected_rating=rating)


@events_bp.route('/<uuid:event_id>')
def event_detail(event_id):
    """Event detail page"""
    event = EventService.get_event_by_id(event_id)

    if not event:
        return "Event not found", 404

    # Get available dates for this event
    available_dates = ShowService.get_available_dates_for_event(event_id)

    # Get theaters showing this event
    shows = ShowService.get_shows_for_event(event_id)
    theater_ids = set(show.auditorium.theater_id for show in shows if show.auditorium)
    theaters = [TheaterService.get_theater_by_id(tid) for tid in theater_ids]

    return render_template('events/detail.html',
                          event=event,
                          available_dates=available_dates,
                          theaters=theaters)
