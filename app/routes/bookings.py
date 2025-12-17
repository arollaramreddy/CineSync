"""
Booking routes - seat selection and booking flow
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.show_service import ShowService
from app.services.event_service import EventService
from app.services.seat_service import SeatService
from app.services.booking_service import BookingService
from app.extensions import db

bookings_bp = Blueprint('bookings', __name__)


@bookings_bp.route('/seats')
def select_seats():
    """Seat selection page"""
    show_id = request.args.get('show_id')
    event_id = request.args.get('event_id')

    if not show_id or not event_id:
        return "Show ID and Event ID required", 400

    show = ShowService.get_show_by_id(show_id, event_id)
    if not show:
        return "Show not found", 404

    event = EventService.get_event_by_id(event_id)
    auditorium = show.auditorium
    theater = auditorium.theater if auditorium else None

    # Get all seats with their booking status
    seats_with_status = SeatService.get_all_seats_with_status(show_id, show.auditorium_id)

    return render_template('bookings/seats.html',
                          show=show,
                          event=event,
                          auditorium=auditorium,
                          theater=theater,
                          seats_with_status=seats_with_status)


@bookings_bp.route('/confirm', methods=['POST'])
def confirm_booking():
    """Booking confirmation page"""
    show_id = request.form.get('show_id')
    event_id = request.form.get('event_id')
    seat_ids = request.form.getlist('seat_ids')

    if not show_id or not event_id or not seat_ids:
        flash('Please select at least one seat', 'error')
        return redirect(url_for('bookings.select_seats',
                              show_id=show_id,
                              event_id=event_id))

    # Check if customer is logged in
    if 'customer_id' not in session:
        # Store booking details in session
        session['pending_booking'] = {
            'show_id': show_id,
            'event_id': event_id,
            'seat_ids': seat_ids
        }
        flash('Please login to continue booking', 'info')
        return redirect(url_for('customers.login'))

    show = ShowService.get_show_by_id(show_id, event_id)
    event = EventService.get_event_by_id(event_id)
    seats = SeatService.get_seats_by_ids(seat_ids)

    # Calculate total
    total_amount = float(show.price) * len(seats)

    return render_template('bookings/confirm.html',
                          show=show,
                          event=event,
                          seats=seats,
                          total_amount=total_amount)


@bookings_bp.route('/create', methods=['POST'])
def create_booking():
    """Create a booking"""
    show_id = request.form.get('show_id')
    event_id = request.form.get('event_id')
    seat_ids = request.form.getlist('seat_ids')

    if 'customer_id' not in session:
        flash('Please login to book', 'error')
        return redirect(url_for('customers.login'))

    customer_id = session['customer_id']

    try:
        booking = BookingService.create_booking(customer_id, show_id, event_id, seat_ids)
        flash('Booking created successfully!', 'success')
        return redirect(url_for('bookings.booking_success', booking_id=booking.booking_id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('bookings.select_seats',
                              show_id=show_id,
                              event_id=event_id))
    except Exception as e:
        db.session.rollback()
        print(f"BOOKING ERROR: {type(e).__name__}: {str(e)}")
        flash(f'An error occurred while creating booking: {str(e)}', 'error')
        return redirect(url_for('bookings.select_seats',
                              show_id=show_id,
                              event_id=event_id))


@bookings_bp.route('/success/<booking_id>')
def booking_success(booking_id):
    """Booking success page"""
    if 'customer_id' not in session:
        return redirect(url_for('customers.login'))

    booking_details = BookingService.get_booking_with_show_details(booking_id)

    if not booking_details:
        return "Booking not found", 404

    # Verify booking belongs to logged-in customer
    if booking_details['booking'].customer_id != session['customer_id']:
        return "Unauthorized", 403

    return render_template('bookings/success.html', **booking_details)


@bookings_bp.route('/<booking_id>')
def booking_detail(booking_id):
    """View booking details"""
    if 'customer_id' not in session:
        return redirect(url_for('customers.login'))

    booking_details = BookingService.get_booking_with_show_details(booking_id)

    if not booking_details:
        return "Booking not found", 404

    # Verify booking belongs to logged-in customer
    if booking_details['booking'].customer_id != session['customer_id']:
        return "Unauthorized", 403

    return render_template('bookings/detail.html', **booking_details)
