# Movie/Event Booking Application

A comprehensive database-driven web application for booking movies, concerts, workshops, and other events. Built with Flask and SQLite, featuring user authentication, seat selection, payment processing, and admin management tools.

## Project Overview

This application provides a complete ticketing platform where users can:
- Register and authenticate
- Browse available movies/events with filters
- View schedules and seat availability
- Make bookings with seat selection
- Process payments
- Manage booking history and cancellations
- Leave reviews and ratings

## Features

### Core Features
✅ **User Management**
- User registration and authentication
- User profile management
- Booking history and notifications

✅ **Movie/Event Listing**
- Browse events with details (title, genre, date, time, venue, price)
- Search and filter functionality
- Event details with reviews and ratings

✅ **Schedule Management**
- Show timings for different venues
- Seat availability tracking
- Venue information management

✅ **Seat Booking & Selection**
- Interactive seat map visualization
- Multiple ticket categories (Regular, VIP, Premium, Balcony)
- Dynamic price calculation based on seat category
- Real-time availability updates

✅ **Booking Management**
- Booking confirmation and details
- Booking status tracking (Pending, Confirmed, Cancelled)
- Booking code generation
- Booking history view

✅ **Payment Tracking**
- Payment status management (Pending, Completed, Refunded)
- Multiple payment modes support
- Transaction tracking
- Refund processing

### Advanced Features
✅ **Admin Panel**
- Dashboard with statistics
- Event management (create, view, edit)
- Venue management
- Show scheduling
- Reports and analytics

✅ **Booking Management**
- Booking cancellation with refunds
- Cancellation reason tracking

✅ **User Reviews & Ratings**
- Rate and review events
- Verified purchases indicator
- Review sorting

✅ **Notifications**
- Booking confirmation notifications
- Booking cancellation alerts
- Upcoming event reminders
- Payment status updates

## Technology Stack

- **Backend**: Python Flask 2.3.3
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login with bcrypt hashing
- **Frontend**: HTML5, CSS3 (Bootstrap 5), JavaScript
- **Forms**: Flask-WTF
- **Environment**: Python 3.8+

## Project Structure

```
movie_booking/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # SQLAlchemy models
│   ├── routes.py                # Application routes
│   ├── templates/
│   │   ├── base.html            # Base template
│   │   ├── index.html           # Home page
│   │   ├── events.html          # Events listing
│   │   ├── event_detail.html    # Event details
│   │   ├── select_seats.html    # Seat selection
│   │   ├── auth/
│   │   │   ├── login.html       # Login page
│   │   │   └── register.html    # Registration page
│   │   ├── booking/
│   │   │   ├── my_bookings.html # User bookings
│   │   │   ├── payment.html     # Payment page
│   │   │   └── booking_details.html
│   │   └── admin/
│   │       ├── dashboard.html   # Admin dashboard
│   │       ├── events.html
│   │       ├── venues.html
│   │       ├── shows.html
│   │       └── reports.html
│   ├── static/
│   │   ├── css/style.css        # Custom styles
│   │   └── js/main.js           # Main JavaScript
├── config.py                    # Configuration settings
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Database Schema

### Models
1. **User** - User accounts with roles (Admin/User)
2. **Event** - Movies/Events with details and ratings
3. **Venue** - Concert halls/theaters with capacity
4. **Screen** - Individual screens/halls in venues
5. **Seat** - Individual seats with categories and availability
6. **Show** - Event showings at specific times/venues
7. **Booking** - User bookings with status tracking
8. **BookedSeat** - Junction table for bookings and seats
9. **Payment** - Payment details and status
10. **Review** - User reviews and ratings
11. **Notification** - System notifications for users

### Enumerations
- **UserRole**: USER, ADMIN
- **EventType**: MOVIE, CONCERT, WORKSHOP, SPORTS, OTHER
- **TicketCategory**: REGULAR, VIP, BALCONY, PREMIUM
- **BookingStatus**: PENDING, CONFIRMED, CANCELLED
- **PaymentStatus**: PENDING, COMPLETED, FAILED, REFUNDED

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone Repository
```bash
cd "c:\Users\venka\OneDrive\Desktop\movie booking"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python run.py
# In another terminal or Flask shell:
python -c "from run import app; app.cli.invoke('init_db')"
# Or use Flask shell:
flask shell
>>> from run import init_db
>>> init_db()
```

This will create:
- Sample venues and screens
- Sample events and shows
- Sample seats with different categories
- Admin user (username: `admin`, password: `admin123`)
- Sample user (username: `user1`, password: `user123`)

### Step 5: Run Application
```bash
python run.py
```

The application will be available at: **http://localhost:5000**

## Usage

### For Users
1. **Register/Login**
   - Create new account or login with existing credentials
   - Use demo account: `user1` / `user123`

2. **Browse Events**
   - Visit Events page to see all available movies/events
   - Use search and filter options
   - Click on an event for detailed information

3. **Book Tickets**
   - Select a show from event details
   - Choose your preferred seats using interactive seat map
   - Review booking summary
   - Proceed to payment

4. **Complete Payment**
   - Select payment method (demo options available)
   - Confirm payment
   - Receive booking confirmation

5. **Manage Bookings**
   - View all your bookings in "My Bookings"
   - View booking details
   - Cancel bookings (with refunds)
   - Leave reviews

### For Administrators
1. **Login as Admin**
   - Use demo account: `admin` / `admin123`
   - Click on "Admin" in navigation

2. **Dashboard**
   - View key statistics
   - See recent bookings
   - Check popular events

3. **Manage Events**
   - Create new events
   - Edit event details
   - Delete events

4. **Manage Venues**
   - Create venues
   - Add screens/halls to venues
   - Configure seating

5. **Schedule Shows**
   - Create shows for events
   - Set dates, times, and prices
   - Configure available seats

6. **View Reports**
   - Analyze bookings by status
   - Revenue tracking by payment mode
   - Top venues by bookings

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Main Content
- `GET /` - Home page
- `GET /events` - Browse events
- `GET /event/<id>` - Event details
- `GET /select-seats/<show_id>` - Seat selection

### Bookings
- `POST /bookings/create` - Create booking
- `GET /bookings/<id>` - Booking details
- `GET /bookings/my-bookings` - User's bookings
- `POST /bookings/cancel/<id>` - Cancel booking
- `GET /bookings/payment/<id>` - Payment page
- `POST /bookings/confirm-payment/<id>` - Process payment

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/events` - Manage events
- `POST /admin/event/create` - Create event
- `GET /admin/venues` - Manage venues
- `POST /admin/venue/create` - Create venue
- `GET /admin/shows` - Manage shows
- `POST /admin/show/create` - Create show
- `GET /admin/reports` - View reports

## Configuration

Edit `config.py` to customize settings:

```python
# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///moviebooking.db'

# Secret Key
SECRET_KEY = 'your-secret-key'

# Session timeout
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Max file size
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

## Security Features

✅ Password hashing with bcrypt
✅ Session management with Flask-Login
✅ CSRF protection on forms
✅ SQL injection prevention with SQLAlchemy
✅ User authentication and authorization
✅ Admin role-based access control

## Future Enhancements

- [ ] Email notifications
- [ ] SMS notifications
- [ ] Real payment gateway integration (Stripe, Razorpay)
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced analytics dashboard
- [ ] Seat analytics with heat maps
- [ ] Bulk booking options
- [ ] Dynamic pricing based on demand
- [ ] Loyalty program
- [ ] Group booking discounts
- [ ] QR code ticket generation
- [ ] Video streaming for "Remember the Titans"
- [ ] Multi-language support
- [ ] Real-time seat availability WebSocket updates

## Database Queries Examples

### Get upcoming shows for an event
```python
from datetime import datetime
shows = Show.query.filter(
    Show.event_id == event_id,
    Show.show_date >= datetime.utcnow()
).order_by(Show.show_date).all()
```

### Get user's bookings with details
```python
bookings = current_user.bookings.filter_by(
    status=BookingStatus.CONFIRMED
).order_by(Booking.booking_date.desc()).all()
```

### Calculate total revenue
```python
from sqlalchemy import func
revenue = db.session.query(
    func.sum(Payment.amount)
).filter(Payment.status == PaymentStatus.COMPLETED).scalar()
```

## Troubleshooting

### Issue: Database not found
**Solution**: Run `flask shell` and execute the `init_db` command

### Issue: Port 5000 already in use
**Solution**: Change port in `run.py` or kill the process using the port

### Issue: Import errors
**Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Issue: Template not found
**Solution**: Ensure the `app/templates` directory exists with proper file structure

## Testing

Currently, the application includes sample data initialization. For comprehensive testing:

1. Create multiple user accounts
2. Book tickets from different users
3. Test cancellations and refunds
4. Create and manage events as admin
5. Generate and view reports

## Contributing

Would you like to contribute? Feel free to:
1. Report bugs
2. Suggest features
3. Improve documentation
4. Optimize code

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions, please check:
- Application logs
- Database state
- Browser console for JavaScript errors
- Flask debug output

## About

Built with ❤️ for efficient event ticketing management.

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Ready for Production
