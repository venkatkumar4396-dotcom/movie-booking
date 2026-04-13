Poster image placement
======================

Drop your poster image files into a workspace-level `uploads/` folder and run:

```
python scripts/assign_posters.py uploads
```

This will copy files into `app/static/img/` using these filename patterns:

- `featured-1.jpg` .. `featured-6.jpg` — used by the homepage carousel
- `trending-1.jpg` .. `trending-8.jpg` — used by the Trending cards on the homepage
- `upcoming-1.jpg` .. `upcoming-6.jpg` — used by the Upcoming shows
- `premium-1.jpg` .. `premium-12.jpg` — used by the Premium page fallback

Alternatively, set `Event.poster_url` in the database to point to an image URL and the site will prefer that.
