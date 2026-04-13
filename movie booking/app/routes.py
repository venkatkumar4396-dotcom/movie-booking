from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import (
    User, Event, Show, Venue, Screen, Seat, Booking, BookedSeat, Payment, 
    Review, Notification, UserRole, BookingStatus, PaymentStatus, EventType
)
from datetime import datetime, timedelta
import random
import string

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
main_bp = Blueprint('main', __name__)
booking_bp = Blueprint('booking', __name__, url_prefix='/bookings')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ==================== AUTHENTICATION ROUTES ====================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is inactive', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            next_page = request.args.get('next')
            
            if user.is_admin():
                return redirect(next_page or url_for('admin.dashboard'))
            else:
                return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('main.index'))

# ==================== MAIN ROUTES ====================

@main_bp.route('/')
def index():
    """Home page with featured events"""
    page = request.args.get('page', 1, type=int)
    events = Event.query.filter_by(is_active=True).paginate(page=page, per_page=12)
    
    # Get upcoming shows
    now = datetime.utcnow()
    upcoming_shows = Show.query.filter(Show.show_date >= now).order_by(Show.show_date).limit(5).all()
    
    return render_template('index.html', events=events, upcoming_shows=upcoming_shows)

@main_bp.route('/premium')
def premium():
    """Premium members page showcasing curated high-tier events"""
    page = request.args.get('page', 1, type=int)

    # Premium heuristics: highly-rated & popular events OR events with expensive shows
    premium_query = Event.query.filter(Event.is_active == True).filter(
        (((Event.average_rating >= 4.5) & (Event.total_reviews >= 50)) | Event.shows.any(Show.base_price >= 500))
    )

    premium_events = premium_query.paginate(page=page, per_page=12)
    return render_template('premium.html', events=premium_events)

@main_bp.route('/events')
def events():
    """Browse all events with filters"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    event_type = request.args.get('type', '')
    city = request.args.get('city', '')
    
    query = Event.query.filter_by(is_active=True)
    
    if search_query:
        query = query.filter(Event.title.ilike(f'%{search_query}%'))
    
    if event_type:
        try:
            event_type_enum = EventType[event_type.upper()]
            query = query.filter_by(event_type=event_type_enum)
        except KeyError:
            # Ignore invalid event type filters
            pass
    
    events = query.paginate(page=page, per_page=12)
    
    # Get unique cities
    cities = db.session.query(Venue.city).distinct().all()
    cities = [c[0] for c in cities]
    
    return render_template('events.html', 
                         events=events, 
                         search_query=search_query, 
                         event_type=event_type,
                         cities=cities)

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    """Event detail page with shows and reviews"""
    event = Event.query.get_or_404(event_id)
    
    # Get shows for this event
    now = datetime.utcnow()
    shows = Show.query.filter(
        Show.event_id == event_id,
        Show.show_date >= now
    ).order_by(Show.show_date).all()
    
    # Group shows by date
    shows_by_date = {}
    for show in shows:
        date_key = show.show_date.date()
        if date_key not in shows_by_date:
            shows_by_date[date_key] = []
        shows_by_date[date_key].append(show)
    
    # Get reviews
    reviews = Review.query.filter_by(event_id=event_id).order_by(Review.created_at.desc()).limit(10).all()
    
    return render_template('event_detail.html', 
                         event=event, 
                         shows_by_date=shows_by_date,
                         reviews=reviews)

@main_bp.route('/select-seats/<int:show_id>')
@login_required
def select_seats(show_id):
    """Seat selection page"""
    show = Show.query.get_or_404(show_id)
    seats = Seat.query.filter_by(screen_id=show.screen_id).order_by(Seat.row, Seat.seat_number).all()
    
    # Get booked seats for this show (excluding cancelled bookings)
    booked_bookings = db.session.query(BookedSeat.seat_id).join(Booking).filter(
        Booking.show_id == show_id,
        Booking.status != BookingStatus.CANCELLED
    ).all()
    booked_seat_ids = {booking[0] for booking in booked_bookings}
    
    # Group seats by row and mark availability
    seats_by_row = {}
    for seat in seats:
        # Seat is booked if it's in booked_seat_ids
        seat.is_available = seat.id not in booked_seat_ids
        
        if seat.row not in seats_by_row:
            seats_by_row[seat.row] = []
        seats_by_row[seat.row].append(seat)
    
    return render_template('select_seats.html', 
                         show=show, 
                         seats_by_row=seats_by_row,
                         booked_seat_ids=booked_seat_ids)

# ==================== BOOKING ROUTES ====================

@booking_bp.route('/create', methods=['POST'])
@login_required
def create_booking():
    """Create a new booking"""
    import json
    
    show_id = request.form.get('show_id', type=int)
    seat_ids = request.form.getlist('seat_ids', type=int)
    seats_data_str = request.form.get('seats_data', '[]')
    
    if not show_id or not seat_ids:
        flash('Please select at least one seat', 'error')
        return redirect(request.referrer or url_for('main.index'))
    
    try:
        seats_data = json.loads(seats_data_str) if seats_data_str else []
    except:
        seats_data = []
    
    show = Show.query.get_or_404(show_id)
    
    # Validate seats and calculate total price
    total_price = 0
    booked_seats_list = []
    
    for seat_id in seat_ids:
        seat = Seat.query.get_or_404(seat_id)
        
        # Validate seat belongs to correct screen
        if seat.screen_id != show.screen_id:
            flash(f'Invalid seat for this show', 'error')
            return redirect(request.referrer)
        
        # Check if seat is actually available (double-check)
        existing_booking = db.session.query(BookedSeat).join(Booking).filter(
            BookedSeat.seat_id == seat_id,
            Booking.show_id == show_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        ).first()
        
        if existing_booking:
            flash(f'Seat {seat.row}{seat.seat_number} is not available', 'error')
            return redirect(request.referrer)
        
        # Get seat category multiplier
        category_multiplier = 1.0
        if seat.category.name == 'VIP':
            category_multiplier = 1.5
        elif seat.category.name == 'PREMIUM':
            category_multiplier = 2.0
        elif seat.category.name == 'BALCONY':
            category_multiplier = 0.75
        
        seat_price = show.base_price * category_multiplier
        total_price += seat_price
        
        booked_seats_list.append({
            'seat': seat,
            'price': seat_price,
            'category': seat.category,
            'multiplier': category_multiplier
        })
    
    if not booked_seats_list:
        flash('No valid seats to book', 'error')
        return redirect(request.referrer)
    
    # Generate unique booking code
    booking_code = f"BK{datetime.utcnow().strftime('%Y%m%d')}" + ''.join(random.choices(string.digits, k=6))
    
    try:
        # Create booking
        booking = Booking(
            user_id=current_user.id,
            show_id=show_id,
            booking_code=booking_code,
            total_price=total_price,
            number_of_tickets=len(seat_ids),
            status=BookingStatus.PENDING
        )
        db.session.add(booking)
        db.session.flush()  # Get booking.id
        
        # Add booked seats
        for seat_info in booked_seats_list:
            booked_seat = BookedSeat(
                booking_id=booking.id,
                seat_id=seat_info['seat'].id,
                price=seat_info['price'],
                category=seat_info['category']
            )
            db.session.add(booked_seat)
            # Mark seat as unavailable in the seats table
            seat_obj = seat_info['seat']
            seat_obj.is_available = False
            db.session.add(seat_obj)
        
        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            user_id=current_user.id,
            amount=total_price,
            status=PaymentStatus.PENDING,
            payment_mode='pending'
        )
        db.session.add(payment)
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            event_id=show.event_id,
            notification_type='booking_created',
            title='Booking Confirmed',
            message=f'Booking {booking_code} created successfully! Proceed to payment.'
        )
        db.session.add(notification)
        # Decrement available seats for the show
        try:
            show.available_seats = (show.available_seats or 0) - len(booked_seats_list)
            if show.available_seats < 0:
                show.available_seats = 0
            db.session.add(show)
        except Exception:
            pass
        
        db.session.commit()
        
        flash(f'Booking created successfully! Booking ID: {booking_code}', 'success')
        return redirect(url_for('booking.payment', booking_id=booking.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating booking: {str(e)}', 'error')
        return redirect(request.referrer)

@booking_bp.route('/payment/<int:booking_id>')
@login_required
def payment(booking_id):
    """Payment page"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('booking/payment.html', booking=booking)

@booking_bp.route('/confirm-payment/<int:booking_id>', methods=['POST'])
@login_required
def confirm_payment(booking_id):
    """Confirm payment and finalize booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    payment_mode = request.form.get('payment_mode')
    
    if not payment_mode:
        return jsonify({'error': 'Payment mode is required'}), 400
    
    # Update payment
    # Ensure a payment record exists
    payment = booking.payment
    if not payment:
        payment = Payment(
            booking_id=booking.id,
            user_id=booking.user_id,
            amount=booking.total_price,
            status=PaymentStatus.COMPLETED,
            payment_mode=payment_mode,
            transaction_id=f'TXN{booking.id}{int(datetime.utcnow().timestamp())}'
        )
        db.session.add(payment)
    else:
        payment.status = PaymentStatus.COMPLETED
        payment.payment_mode = payment_mode
        payment.transaction_id = f'TXN{booking.id}{int(datetime.utcnow().timestamp())}'
    
    # Update booking
    booking.status = BookingStatus.CONFIRMED
    
    # Create confirmation notification
    notification = Notification(
        user_id=current_user.id,
        event_id=booking.show.event_id,
        notification_type='booking_confirmed',
        title='Booking Confirmed',
        message=f'Your booking {booking.booking_code} is confirmed!'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Payment successful! Your booking is confirmed.', 'success')
    return redirect(url_for('booking.booking_details', booking_id=booking.id))

@booking_bp.route('/<int:booking_id>')
@login_required
def booking_details(booking_id):
    """View booking details"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id and not current_user.is_admin():
        flash('Unauthorized', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('booking/booking_details.html', booking=booking)

@booking_bp.route('/my-bookings')
@login_required
def my_bookings():
    """View all user bookings"""
    page = request.args.get('page', 1, type=int)
    bookings = current_user.bookings.order_by(Booking.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('booking/my_bookings.html', bookings=bookings)

@booking_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if booking.status == BookingStatus.CANCELLED:
        return jsonify({'error': 'Booking is already cancelled'}), 400
    
    cancellation_reason = request.form.get('reason')
    
    # Update booking
    booking.status = BookingStatus.CANCELLED
    booking.cancelled_date = datetime.utcnow()
    booking.cancellation_reason = cancellation_reason
    
    # Process refund
    if booking.payment and booking.payment.status == PaymentStatus.COMPLETED:
        booking.payment.status = PaymentStatus.REFUNDED
        booking.payment.refund_amount = booking.total_price
        booking.payment.refund_date = datetime.utcnow()
        booking.payment.refund_reason = cancellation_reason
    
    # Make seats available again
    for booked_seat in booking.booked_seats:
        booked_seat.seat.is_available = True
    # Restore available seats count on the show
    try:
        if booking.show and booking.number_of_tickets:
            booking.show.available_seats = (booking.show.available_seats or 0) + booking.number_of_tickets
            db.session.add(booking.show)
    except Exception:
        pass
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        event_id=booking.show.event_id,
        notification_type='booking_cancelled',
        title='Booking Cancelled',
        message=f'Your booking {booking.booking_code} has been cancelled.'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('booking.my_bookings'))

# ==================== ADMIN ROUTES ====================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    # Get statistics
    total_users = User.query.count()
    total_events = Event.query.count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    # Popular events
    popular_events = db.session.query(
        Event.id, Event.title, db.func.count(Booking.id).label('booking_count')
    ).join(Show, Event.id == Show.event_id).join(
        Booking, Show.id == Booking.show_id
    ).group_by(Event.id).order_by(
        db.func.count(Booking.id).desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_events=total_events,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings,
                         popular_events=popular_events)

@admin_bp.route('/events')
@login_required
def manage_events():
    """Manage events"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    events = Event.query.paginate(page=page, per_page=20)
    
    return render_template('admin/events.html', events=events)

@admin_bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create new event"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Safely parse event type and release date
        event_type_str = request.form.get('event_type', 'MOVIE') or 'MOVIE'
        try:
            event_type_enum = EventType[event_type_str.upper()]
        except KeyError:
            event_type_enum = EventType.MOVIE

        release_date_str = request.form.get('release_date')
        try:
            release_date = datetime.fromisoformat(release_date_str) if release_date_str else datetime.utcnow()
        except ValueError:
            flash('Invalid release date format', 'error')
            return redirect(url_for('admin.create_event'))

        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            event_type=event_type_enum,
            genre=request.form.get('genre'),
            duration_minutes=request.form.get('duration_minutes', type=int),
            language=request.form.get('language'),
            rating=request.form.get('rating'),
            poster_url=request.form.get('poster_url'),
            release_date=release_date
        )

        db.session.add(event)
        db.session.commit()

        flash('Event created successfully', 'success')
        return redirect(url_for('admin.manage_events'))
    
    return render_template('admin/create_event.html')

@admin_bp.route('/venues')
@login_required
def manage_venues():
    """Manage venues"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    venues = Venue.query.all()
    return render_template('admin/venues.html', venues=venues)

@admin_bp.route('/venue/create', methods=['GET', 'POST'])
@login_required
def create_venue():
    """Create new venue"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        venue = Venue(
            name=request.form.get('name'),
            city=request.form.get('city'),
            address=request.form.get('address'),
            capacity=request.form.get('capacity', type=int),
            amenities=request.form.get('amenities')
        )
        
        db.session.add(venue)
        db.session.commit()
        
        flash('Venue created successfully', 'success')
        return redirect(url_for('admin.manage_venues'))
    
    return render_template('admin/create_venue.html')

@admin_bp.route('/shows')
@login_required
def manage_shows():
    """Manage shows"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    shows = Show.query.order_by(Show.show_date.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/shows.html', shows=shows)

@admin_bp.route('/show/create', methods=['GET', 'POST'])
@login_required
def create_show():
    """Create new show"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Parse dates/times safely
        try:
            show_date_str = request.form.get('show_date')
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')

            show_date = datetime.fromisoformat(show_date_str) if show_date_str else None
            start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
            end_time = datetime.fromisoformat(end_time_str) if end_time_str else None

            if not all([show_date, start_time, end_time]):
                flash('Show date, start time and end time are required', 'error')
                return redirect(url_for('admin.create_show'))
        except ValueError:
            flash('Invalid date/time format', 'error')
            return redirect(url_for('admin.create_show'))
        
        screen = Screen.query.get_or_404(request.form.get('screen_id', type=int))

        show = Show(
            event_id=request.form.get('event_id', type=int),
            venue_id=screen.venue_id,
            screen_id=screen.id,
            show_date=show_date,
            start_time=start_time,
            end_time=end_time,
            available_seats=screen.total_seats,
            base_price=request.form.get('base_price', type=float)
        )
        
        db.session.add(show)
        db.session.commit()
        
        flash('Show created successfully', 'success')
        return redirect(url_for('admin.manage_shows'))
    
    events = Event.query.all()
    venues = Venue.query.all()
    screens = []
    
    if request.method == 'GET' and request.args.get('venue_id'):
        screens = Screen.query.filter_by(venue_id=request.args.get('venue_id', type=int)).all()
    
    return render_template('admin/create_show.html', 
                         events=events, 
                         venues=venues,
                         screens=screens)

@admin_bp.route('/reports')
@login_required
def reports():
    """View reports"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    # Total bookings by status
    bookings_by_status = db.session.query(
        Booking.status, db.func.count(Booking.id)
    ).group_by(Booking.status).all()
    
    # Revenue by payment mode
    revenue_by_mode = db.session.query(
        Payment.payment_mode, db.func.sum(Payment.amount)
    ).filter(Payment.status == PaymentStatus.COMPLETED).group_by(Payment.payment_mode).all()
    
    # Top venues
    top_venues = db.session.query(
        Venue.name, db.func.count(Booking.id).label('total_bookings')
    ).join(Show, Venue.id == Show.venue_id).join(
        Booking, Show.id == Booking.show_id
    ).group_by(Venue.id).order_by(
        db.func.count(Booking.id).desc()
    ).limit(10).all()
    
    return render_template('admin/reports.html',
                         bookings_by_status=bookings_by_status,
                         revenue_by_mode=revenue_by_mode,
                         top_venues=top_venues)
