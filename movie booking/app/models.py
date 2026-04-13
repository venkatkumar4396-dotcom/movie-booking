from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

class UserRole(enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"

class BookingStatus(enum.Enum):
    """Booking status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class PaymentStatus(enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class EventType(enum.Enum):
    """Event type enumeration"""
    MOVIE = "movie"
    CONCERT = "concert"
    WORKSHOP = "workshop"
    SPORTS = "sports"
    OTHER = "other"

class TicketCategory(enum.Enum):
    """Ticket category enumeration"""
    REGULAR = "regular"
    VIP = "vip"
    BALCONY = "balcony"
    PREMIUM = "premium"

# ==================== USER MODEL ====================
class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== VENUE MODEL ====================
class Venue(db.Model):
    """Venue model for storing venue information"""
    __tablename__ = 'venues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    city = db.Column(db.String(120), nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    amenities = db.Column(db.Text)  # JSON string of amenities
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shows = db.relationship('Show', backref='venue', lazy='dynamic', cascade='all, delete-orphan')
    screens = db.relationship('Screen', backref='venue', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Venue {self.name}>'

# ==================== SCREEN MODEL ====================
class Screen(db.Model):
    """Screen/Hall model within a venue"""
    __tablename__ = 'screens'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    screen_number = db.Column(db.Integer, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    columns = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    seats = db.relationship('Seat', backref='screen', lazy='dynamic', cascade='all, delete-orphan')
    shows = db.relationship('Show', backref='screen', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Screen {self.venue.name} - {self.screen_number}>'

# ==================== SEAT MODEL ====================
class Seat(db.Model):
    """Seat model for tracking individual seats"""
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    screen_id = db.Column(db.Integer, db.ForeignKey('screens.id'), nullable=False)
    row = db.Column(db.String(5), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    category = db.Column(db.Enum(TicketCategory), default=TicketCategory.REGULAR, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    bookings = db.relationship('BookedSeat', backref='seat', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('screen_id', 'row', 'seat_number', name='unique_seat_per_screen'),)
    
    def __repr__(self):
        return f'<Seat {self.row}{self.seat_number}>'

# ==================== EVENT/MOVIE MODEL ====================
class Event(db.Model):
    """Event/Movie model"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    event_type = db.Column(db.Enum(EventType), default=EventType.MOVIE, nullable=False)
    genre = db.Column(db.String(100))
    duration_minutes = db.Column(db.Integer)
    language = db.Column(db.String(50))
    rating = db.Column(db.String(10))  # G, PG, PG-13, R, etc.
    poster_url = db.Column(db.String(500))
    release_date = db.Column(db.DateTime, nullable=False)
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shows = db.relationship('Show', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Event {self.title}>'

# ==================== SHOW MODEL ====================
class Show(db.Model):
    """Show/Screening model"""
    __tablename__ = 'shows'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    screen_id = db.Column(db.Integer, db.ForeignKey('screens.id'), nullable=False)
    show_date = db.Column(db.DateTime, nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='show', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Show {self.event.title} at {self.show_date}>'

# ==================== BOOKING MODEL ====================
class Booking(db.Model):
    """Booking model"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('shows.id'), nullable=False)
    booking_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    number_of_tickets = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cancelled_date = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booked_seats = db.relationship('BookedSeat', backref='booking', lazy='dynamic', cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='booking', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Booking {self.booking_code}>'

# ==================== BOOKED SEAT MODEL ====================
class BookedSeat(db.Model):
    """Booked seat model (junction for booking and seat)"""
    __tablename__ = 'booked_seats'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.Enum(TicketCategory), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (db.UniqueConstraint('booking_id', 'seat_id', name='unique_booking_seat'),)
    
    def __repr__(self):
        return f'<BookedSeat Booking#{self.booking_id} Seat#{self.seat_id}>'

# ==================== PAYMENT MODEL ====================
class Payment(db.Model):
    """Payment model"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_mode = db.Column(db.String(50), nullable=False)  # credit_card, debit_card, upi, wallet, etc.
    transaction_id = db.Column(db.String(100), unique=True)
    refund_amount = db.Column(db.Float, default=0.0)
    refund_date = db.Column(db.DateTime)
    refund_reason = db.Column(db.Text)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'

# ==================== REVIEW MODEL ====================
class Review(db.Model):
    """Review and rating model"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # User has actually booked this event
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='unique_review_per_user_event'),)
    
    def __repr__(self):
        return f'<Review {self.id}>'

# ==================== NOTIFICATION MODEL ====================
class Notification(db.Model):
    """Notification model for reminders and alerts"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    notification_type = db.Column(db.String(50), nullable=False)  # booking_confirmation, reminder, cancellation, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Notification {self.id}>'
