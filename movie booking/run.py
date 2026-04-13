import os
from app import create_app, db
from app.models import User, Event, Venue, Show, Screen, Seat, Booking, BookedSeat, Payment, Review, Notification

# Create the Flask app
app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Context for Flask shell"""
    return {
        'db': db,
        'User': User,
        'Event': Event,
        'Venue': Venue,
        'Show': Show,
        'Screen': Screen,
        'Seat': Seat,
        'Booking': Booking,
        'BookedSeat': BookedSeat,
        'Payment': Payment,
        'Review': Review,
        'Notification': Notification
    }

@app.cli.command()
def init_db():
    """Initialize database with sample data"""
    db.create_all()
    
    # Create sample venues
    venues_data = [
        {'name': 'Cineplex Downtown', 'city': 'New York', 'address': '123 Main St', 'capacity': 500},
        {'name': 'Star Theater', 'city': 'Los Angeles', 'address': '456 Oak Ave', 'capacity': 400},
        {'name': 'Grand Cinema', 'city': 'Chicago', 'address': '789 Park Rd', 'capacity': 350},
    ]
    
    for venue_data in venues_data:
        if not Venue.query.filter_by(name=venue_data['name']).first():
            venue = Venue(**venue_data)
            db.session.add(venue)
    
    db.session.commit()
    
    # Create screens for each venue
    venues = Venue.query.all()
    for venue in venues:
        for screen_num in range(1, 4):
            if not Screen.query.filter_by(venue_id=venue.id, screen_number=screen_num).first():
                screen = Screen(
                    venue_id=venue.id,
                    screen_number=screen_num,
                    total_seats=100,
                    rows=10,
                    columns=10
                )
                db.session.add(screen)
    
    db.session.commit()
    
    # Create sample events
    from datetime import datetime, timedelta
    
    events_data = [
        {
            'title': 'Avengers: Endgame',
            'description': 'Marvel superhero blockbuster',
            'event_type': 'MOVIE',
            'genre': 'Action',
            'duration_minutes': 181,
            'language': 'English',
            'rating': 'PG-13',
            'poster_url': 'https://via.placeholder.com/300x450',
            'release_date': datetime.utcnow() + timedelta(days=1)
        },
        {
            'title': 'The Lion King',
            'description': 'Disney animated classic',
            'event_type': 'MOVIE',
            'genre': 'Animation',
            'duration_minutes': 118,
            'language': 'English',
            'rating': 'G',
            'poster_url': 'https://via.placeholder.com/300x450',
            'release_date': datetime.utcnow() + timedelta(days=3)
        },
        {
            'title': 'Taylor Swift: The Eras Tour',
            'description': 'Live concert experience',
            'event_type': 'CONCERT',
            'genre': 'Music',
            'duration_minutes': 180,
            'language': 'English',
            'rating': 'PG',
            'poster_url': 'https://via.placeholder.com/300x450',
            'release_date': datetime.utcnow() + timedelta(days=5)
        },
    ]
    
    for event_data in events_data:
        if not Event.query.filter_by(title=event_data['title']).first():
            event = Event(**event_data)
            db.session.add(event)
    
    db.session.commit()
    
    # Create shows for events
    from app.models import EventType
    events = Event.query.all()
    screens = Screen.query.all()
    
    for event in events:
        for screen in screens[:2]:
            show_date = event.release_date
            show = Show(
                event_id=event.id,
                venue_id=screen.venue_id,
                screen_id=screen.id,
                show_date=show_date,
                start_time=show_date.replace(hour=18),
                end_time=show_date.replace(hour=20),
                available_seats=screen.total_seats,
                base_price=15.0
            )
            db.session.add(show)
    
    db.session.commit()
    
    # Create seats for each screen
    screens = Screen.query.all()
    from app.models import TicketCategory
    
    for screen in screens:
        for row_num in range(screen.rows):
            for col_num in range(screen.columns):
                row_letter = chr(65 + row_num)
                seat_num = col_num + 1
                
                # Assign categories based on position
                if row_num < 2:
                    category = TicketCategory.VIP
                elif row_num == screen.rows - 1:
                    category = TicketCategory.BALCONY
                elif col_num == 0 or col_num == screen.columns - 1:
                    category = TicketCategory.PREMIUM
                else:
                    category = TicketCategory.REGULAR
                
                seat = Seat(
                    screen_id=screen.id,
                    row=row_letter,
                    seat_number=seat_num,
                    category=category
                )
                db.session.add(seat)
    
    db.session.commit()
    
    # Create admin user
    if not User.query.filter_by(username='admin').first():
        from app.models import UserRole
        admin = User(
            username='admin',
            email='admin@moviebooking.com',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Create sample user
    if not User.query.filter_by(username='user1').first():
        user = User(
            username='user1',
            email='user1@moviebooking.com',
            first_name='John',
            last_name='Doe'
        )
        user.set_password('user123')
        db.session.add(user)
    
    db.session.commit()
    
    print("Database initialized successfully!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
