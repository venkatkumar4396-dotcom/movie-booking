#!/usr/bin/env python3
"""
update_poster_urls.py

Update event poster_url fields to use local static images.
This maps the first 12 active events to featured-X and trending-X images.
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Event

def main():
    app = create_app()
    with app.app_context():
        # Get first 6 featured events
        featured = Event.query.filter_by(is_active=True).order_by(Event.created_at.desc()).limit(6).all()
        for i, event in enumerate(featured, 1):
            event.poster_url = f'/static/img/featured-{i}.jpg'
            print(f'Event {event.id} ({event.title}) -> featured-{i}.jpg')
        
        # Get next 6 trending events
        trending = Event.query.filter_by(is_active=True).order_by(Event.created_at.desc()).offset(6).limit(6).all()
        for i, event in enumerate(trending, 1):
            event.poster_url = f'/static/img/trending-{i}.jpg'
            print(f'Event {event.id} ({event.title}) -> trending-{i}.jpg')
        
        db.session.commit()
        print('\nDone. Poster URLs updated in database.')

if __name__ == '__main__':
    main()
