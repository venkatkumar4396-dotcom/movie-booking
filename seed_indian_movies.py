"""
Script to populate the Movie Booking Application with Indian Movies
Run: python seed_indian_movies.py
"""

import os
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    User, Event, Venue, Show, Screen, Seat, Booking, BookedSeat, 
    Payment, Review, Notification, UserRole, EventType, TicketCategory
)

# Create app context
app = create_app('development')

def seed_indian_movies():
    """Populate database with Indian movies and related data"""
    
    with app.app_context():
        # Clear existing data (optional - comment out to keep existing data)
        # db.drop_all()
        # db.create_all()
        
        print("🎬 Starting to seed Indian movies database...")
        
        # ==================== CREATE VENUES ====================
        print("\n📍 Creating venues...")
        
        venues_data = [
            {
                'name': 'PVR Cinemas Bangalore',
                'city': 'Bangalore',
                'address': 'Forum Mall, Bengaluru, Karnataka 560001',
                'capacity': 500,
                'amenities': 'IMAX, 4DX, WiFi, Parking, F&B'
            },
            {
                'name': 'Inox Mumbai Downtown',
                'city': 'Mumbai',
                'address': 'High Street Phoenix, Lower Parel, Mumbai 400013',
                'capacity': 600,
                'amenities': '4K Projection, Dolby Atmos, Premium Seating, WiFi, Cafe'
            },
            {
                'name': 'Cinépolis Delhi NCR',
                'city': 'Delhi',
                'address': 'DLF CyberHub, Gurugram, Haryana 122001',
                'capacity': 450,
                'amenities': '4DX, Dolby Cinema, Recliner Seats, WiFi, Food Court'
            },
            {
                'name': 'SPI Chennai',
                'city': 'Chennai',
                'address': 'Express Avenue, Chennai, Tamil Nadu 600002',
                'capacity': 400,
                'amenities': 'IMAX, Premium Seating, WiFi, Parking, Restaurant'
            },
            {
                'name': 'Carnival Kolkata',
                'city': 'Kolkata',
                'address': 'South City Mall, Kolkata, West Bengal 700105',
                'capacity': 350,
                'amenities': '4K Screen, Dolby Atmos, Comfort Seating, WiFi'
            },
            {
                'name': 'AFSPA Hyderabad',
                'city': 'Hyderabad',
                'address': 'Prasads IMAX, Hyderabad, Telangana 500034',
                'capacity': 480,
                'amenities': 'IMAX 3D, Premium Sound, Reclining Seats, Parking'
            }
        ]
        
        venues = {}
        for venue_data in venues_data:
            existing = Venue.query.filter_by(name=venue_data['name']).first()
            if not existing:
                venue = Venue(**venue_data)
                db.session.add(venue)
                venues[venue_data['name']] = venue
            else:
                venues[venue_data['name']] = existing
        
        db.session.commit()
        print(f"✅ Created {len(venues)} venues")
        
        # ==================== CREATE SCREENS ====================
        print("\n🎞️ Creating screens...")
        
        for venue_name, venue in venues.items():
            for screen_num in range(1, 5):
                existing = Screen.query.filter_by(venue_id=venue.id, screen_number=screen_num).first()
                if not existing:
                    screen = Screen(
                        venue_id=venue.id,
                        screen_number=screen_num,
                        total_seats=100,
                        rows=10,
                        columns=10
                    )
                    db.session.add(screen)
        
        db.session.commit()
        print("✅ Created screens for all venues")
        
        # ==================== CREATE SEATS ====================
        print("\n💺 Creating seats...")
        
        screens = Screen.query.all()
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
                    
                    existing = Seat.query.filter_by(
                        screen_id=screen.id,
                        row=row_letter,
                        seat_number=seat_num
                    ).first()
                    
                    if not existing:
                        seat = Seat(
                            screen_id=screen.id,
                            row=row_letter,
                            seat_number=seat_num,
                            category=category
                        )
                        db.session.add(seat)
        
        db.session.commit()
        print("✅ Created seats for all screens")
        
        # ==================== CREATE INDIAN MOVIES ====================
        print("\n🎬 Creating Indian movies...")
        
        now = datetime.utcnow()
        
        indian_movies = [
            {
                'title': 'Pushpa 2: The Rule',
                'description': 'Allu Arjun reprises his role in this highly anticipated sequel about a smuggler\'s rise to power.',
                'genre': 'Action/Thriller',
                'language': 'Telugu',
                'duration_minutes': 200,
                'rating': 'UA',
                'poster_url': 'https://via.placeholder.com/300x450?text=Pushpa+2',
                'release_date': now + timedelta(days=1)
            },
            {
                'title': 'Khel Khel Mein',
                'description': 'A comedy-thriller featuring Akshay Kumar and ensemble cast, depicting a day in the life of regular people.',
                'genre': 'Comedy/Thriller',
                'language': 'Hindi',
                'duration_minutes': 115,
                'rating': 'U',
                'poster_url': 'https://via.placeholder.com/300x450?text=Khel+Khel+Mein',
                'release_date': now + timedelta(days=2)
            },
            {
                'title': 'Tillu Square',
                'description': 'Siddhant Chaturvedi leads this action-comedy about a con artist in pursuit of a perfect scam.',
                'genre': 'Action/Comedy',
                'language': 'Hindi',
                'duration_minutes': 128,
                'rating': 'U',
                'poster_url': 'https://via.placeholder.com/300x450?text=Tillu+Square',
                'release_date': now + timedelta(days=3)
            },
            {
                'title': 'Article 370',
                'description': 'A gripping thriller based on the constitutional decision that changed Kashmir\'s status.',
                'genre': 'Thriller/Drama',
                'language': 'Hindi',
                'duration_minutes': 160,
                'rating': 'UA',
                'poster_url': 'https://via.placeholder.com/300x450?text=Article+370',
                'release_date': now + timedelta(days=4)
            },
            {
                'title': 'Satyaprem Ki Katha',
                'description': 'Kartik Aaryan and Kiara Advani star in this romantic drama exploring relationships in the modern era.',
                'genre': 'Romance/Drama',
                'language': 'Hindi',
                'duration_minutes': 142,
                'rating': 'U',
                'poster_url': 'https://via.placeholder.com/300x450?text=Satyaprem+Ki+Katha',
                'release_date': now + timedelta(days=5)
            },
            {
                'title': 'Teri Baaton Mein Aisa Uljha Jiya',
                'description': 'A sci-fi romantic comedy starring Shahid Kapoor opposite an AI robot.',
                'genre': 'Sci-Fi/Romance/Comedy',
                'language': 'Hindi',
                'duration_minutes': 184,
                'rating': 'U',
                'poster_url': 'https://via.placeholder.com/300x450?text=Teri+Baaton+Mein',
                'release_date': now + timedelta(days=6)
            },
            {
                'title': 'Jawan',
                'description': 'Shah Rukh Khan returns to cinema with this high-octane action thriller by Sanjay Leela Bhansali.',
                'genre': 'Action/Thriller',
                'language': 'Hindi',
                'duration_minutes': 169,
                'rating': 'UA',
                'poster_url': 'https://via.placeholder.com/300x450?text=Jawan',
                'release_date': now + timedelta(days=7)
            },
            {
                'title': 'Dunki',
                'description': 'Shah Rukh Khan and Taapsee Pannu in a story about illegally traveling to another country.',
                'genre': 'Comedy/Drama',
                'language': 'Hindi',
                'duration_minutes': 155,
                'rating': 'U',
                'poster_url': 'https://via.placeholder.com/300x450?text=Dunki',
                'release_date': now + timedelta(days=8)
            },
            {
                'title': 'Pathaan',
                'description': 'Shah Rukh Khan, Deepika Padukone, and John Abraham in an espionage thriller.',
                'genre': 'Action/Thriller',
                'language': 'Hindi',
                'duration_minutes': 146,
                'rating': 'U',
                'poster_url': 'https://via.placeholder.com/300x450?text=Pathaan',
                'release_date': now + timedelta(days=9)
            },
            {
                'title': 'Animal',
                'description': 'Ranbir Kapoor in a dark crime drama exploring the complexities of father-son relationships.',
                'genre': 'Crime/Drama',
                'language': 'Hindi',
                'duration_minutes': 203,
                'rating': 'UA',
                'poster_url': 'https://via.placeholder.com/300x450?text=Animal',
                'release_date': now + timedelta(days=10)
            },
            {
                'title': 'Gadar 2',
                'description': 'Sunny Deol reprises his iconic action role in this patriotic sequel set during the India-Pakistan divide.',
                'genre': 'Action/Patriotic',
                'language': 'Hindi',
                'duration_minutes': 179,
                'rating': 'UA',
                'poster_url': 'https://via.placeholder.com/300x450?text=Gadar+2',
                'release_date': now + timedelta(days=11)
            },
            {
                'title': 'Bhaiyya Ji',
                'description': 'Manoj Bajpayee in this satirical thriller about a goon turned political aspirant.',
                'genre': 'Thriller/Comedy',
                'language': 'Hindi',
                'duration_minutes': 120,
                'rating': 'UA',
                'poster_url': 'https://via.placeholder.com/300x450?text=Bhaiyya+Ji',
                'release_date': now + timedelta(days=12)
            },
            {
                'title': 'Brahmastra Part One: Shiva',
                'description': 'Ranbir Kapoor and Alia Bhatt in Ayan Mukerji\'s mega action-fantasy epic.',
                'genre': 'Action/Fantasy',
                'language': 'Hindi',
                'duration_minutes': 167,
                'rating': 'UA',
                'poster_url': 'https://via.placeholder.com/300x450?text=Brahmastra',
                'release_date': now + timedelta(days=13)
            },
            {
                'title': 'Maidaan',
                'description': 'Ajay Devgn stars as football coach Syed Abdul Rahim in this inspirational sports drama.',
                'genre': 'Sports/Drama',
                'language': 'Hindi',
                'duration_minutes': 160,
                'rating': 'U',
                'poster_url': 'https://via.placeholder.com/300x450?text=Maidaan',
                'release_date': now + timedelta(days=14)
            }
        ]
        
        events = {}
        for movie_data in indian_movies:
            existing = Event.query.filter_by(title=movie_data['title']).first()
            if not existing:
                event = Event(
                    title=movie_data['title'],
                    description=movie_data['description'],
                    event_type=EventType.MOVIE,
                    genre=movie_data['genre'],
                    language=movie_data['language'],
                    duration_minutes=movie_data['duration_minutes'],
                    rating=movie_data['rating'],
                    poster_url=movie_data['poster_url'],
                    release_date=movie_data['release_date'],
                    is_active=True
                )
                db.session.add(event)
                events[movie_data['title']] = event
            else:
                events[movie_data['title']] = existing
        
        db.session.commit()
        print(f"✅ Created {len(events)} Indian movies")
        
        # ==================== CREATE SHOWS ====================
        print("\n� Creating shows for Indian movies...")
        
        show_count = 0
        for event_title, event in events.items():
            # Create 2-3 shows per movie in different venues
            venues_list = list(venues.values())
            for i in range(2):
                venue = venues_list[i % len(venues_list)]
                screens_in_venue = Screen.query.filter_by(venue_id=venue.id).all()
                
                if screens_in_venue:
                    screen = screens_in_venue[i % len(screens_in_venue)]
                    
                    # Create show for the movie release date
                    show_date = event.release_date
                    show_times = ['10:00', '13:30', '18:00', '21:00']
                    
                    for time_idx in range(2):  # Create 2 shows per day
                        show_time_str = show_times[time_idx]
                        start_hour = int(show_time_str.split(':')[0])
                        start_minute = int(show_time_str.split(':')[1])
                        
                        start_time = show_date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                        end_time = start_time + timedelta(minutes=event.duration_minutes)
                        
                        existing_show = Show.query.filter_by(
                            event_id=event.id,
                            venue_id=venue.id,
                            screen_id=screen.id,
                            start_time=start_time
                        ).first()
                        
                        if not existing_show:
                            show = Show(
                                event_id=event.id,
                                venue_id=venue.id,
                                screen_id=screen.id,
                                show_date=show_date,
                                start_time=start_time,
                                end_time=end_time,
                                available_seats=screen.total_seats,
                                base_price=150.0,  # Base price ₹150
                                is_active=True
                            )
                            db.session.add(show)
                            show_count += 1
        
        db.session.commit()
        print(f"✅ Created {show_count} shows")
        
        # ==================== CREATE SAMPLE REVIEWS ====================
        print("\n⭐ Creating sample reviews...")
        
        # Create or get demo user
        demo_user = User.query.filter_by(username='user1').first()
        if not demo_user:
            demo_user = User(
                username='user1',
                email='user1@moviebooking.com',
                first_name='John',
                last_name='Doe'
            )
            demo_user.set_password('user123')
            db.session.add(demo_user)
            db.session.commit()
        
        review_texts = [
            "Amazing performance by the lead actor! Must watch!",
            "Great storyline with excellent cinematography.",
            "Perfect blend of action and emotions. Highly recommended!",
            "One of the best Indian movies I've seen recently.",
            "Outstanding direction and screenplay. Worth every penny!",
            "Thrilling from start to finish. Absolutely loved it!",
            "Great entertainment for the whole family.",
            "Impressive technical aspects. A true cinematic experience!"
        ]
        
        review_count = 0
        for event in list(events.values())[:5]:  # Add reviews for first 5 movies
            existing_review = Review.query.filter_by(
                event_id=event.id,
                user_id=demo_user.id
            ).first()
            
            if not existing_review:
                review = Review(
                    event_id=event.id,
                    user_id=demo_user.id,
                    rating=4 + (review_count % 2),  # 4 or 5 stars
                    review_text=review_texts[review_count % len(review_texts)],
                    is_verified=True
                )
                db.session.add(review)
                review_count += 1
                
                # Update event average rating
                event.average_rating = 4.5
                event.total_reviews = review_count
        
        db.session.commit()
        print(f"✅ Created {review_count} reviews")
        
        # ==================== SUMMARY ====================
        print("\n" + "="*50)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("="*50)
        print(f"\n📊 Summary:")
        print(f"   • Venues: {len(venues)}")
        print(f"   • Screens: {Screen.query.count()}")
        print(f"   • Seats: {Seat.query.count()}")
        print(f"   • Indian Movies: {len(events)}")
        print(f"   • Shows: {show_count}")
        print(f"   • Reviews: {review_count}")
        
        print(f"\n🎬 Movies added:")
        for movie_title in events.keys():
            print(f"   ✓ {movie_title}")
        
        print("\n🎯 Quick Links:")
        print("   📍 Venues: Bangalore, Mumbai, Delhi, Chennai, Kolkata, Hyderabad")
        print("   🌐 Browse: http://localhost:5000/events")
        print("   👤 Demo User: user1 / user123")
        print("\n" + "="*50)

if __name__ == '__main__':
    seed_indian_movies()
