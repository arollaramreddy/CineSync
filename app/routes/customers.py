"""
Customer routes - authentication and profile
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.customer import Customer
from app.services.booking_service import BookingService
from app.extensions import db
import uuid

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login"""
    if request.method == 'POST':
        email = request.form.get('email')

        customer = Customer.query.filter_by(email=email).first()

        if customer:
            session['customer_id'] = customer.customer_id
            session['customer_name'] = customer.name
            session.permanent = True

            flash(f'Welcome back, {customer.name}!', 'success')

            # Check for pending booking
            if 'pending_booking' in session:
                pending = session.pop('pending_booking')
                return redirect(url_for('bookings.confirm_booking',
                                      show_id=pending['show_id'],
                                      event_id=pending['event_id'],
                                      seat_ids=pending['seat_ids']))

            return redirect(url_for('customers.profile'))
        else:
            flash('Email not found. Please register.', 'error')

    return render_template('customers/login.html')


@customers_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Check if email exists
        existing = Customer.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('customers.login'))

        # Create new customer
        customer_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"
        customer = Customer(
            customer_id=customer_id,
            name=name,
            email=email,
            phone=phone
        )

        try:
            db.session.add(customer)
            db.session.commit()

            # Auto login
            session['customer_id'] = customer.customer_id
            session['customer_name'] = customer.name
            session.permanent = True

            flash('Registration successful!', 'success')

            # Check for pending booking
            if 'pending_booking' in session:
                pending = session.pop('pending_booking')
                return redirect(url_for('bookings.confirm_booking',
                                      show_id=pending['show_id'],
                                      event_id=pending['event_id'],
                                      seat_ids=pending['seat_ids']))

            return redirect(url_for('customers.profile'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'error')

    return render_template('customers/register.html')


@customers_bp.route('/logout')
def logout():
    """Customer logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


@customers_bp.route('/profile')
def profile():
    """Customer profile and booking history"""
    if 'customer_id' not in session:
        return redirect(url_for('customers.login'))

    customer_id = session['customer_id']
    customer = Customer.query.get(customer_id)

    if not customer:
        session.clear()
        return redirect(url_for('customers.login'))

    # Get booking history with details
    bookings = BookingService.get_customer_bookings(customer_id)

    bookings_with_details = []
    for booking in bookings:
        details = BookingService.get_booking_with_show_details(booking.booking_id)
        if details:
            bookings_with_details.append(details)

    return render_template('customers/profile.html',
                          customer=customer,
                          bookings=bookings_with_details)
