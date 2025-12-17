"""
Main routes - homepage and search
"""
from flask import Blueprint, render_template, request
from app.services.event_service import EventService
from app.services.theater_service import TheaterService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage"""
    featured_events = EventService.get_featured_events(limit=6)
    event_types = EventService.get_event_types()
    cities = TheaterService.get_cities()

    return render_template('index.html',
                          featured_events=featured_events,
                          event_types=event_types,
                          cities=cities)


@main_bp.route('/search')
def search():
    """Search events and theaters"""
    query = request.args.get('q', '').strip()

    if not query:
        return render_template('search.html', events=[], theaters=[])

    events = EventService.search_events(query)
    theaters = TheaterService.search_theaters(query)

    return render_template('search.html',
                          query=query,
                          events=events,
                          theaters=theaters)
