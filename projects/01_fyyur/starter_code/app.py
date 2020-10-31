#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_talent_message = db.Column(db.String(120))
    shows = db.relationship("Show", backref="venue")

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_venue_message = db.Column(db.String(120))
    shows = db.relationship("Show", backref="artist")

class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, datetime):
    date = value
  else:
    date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en_US')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Random Utility Functions.
#----------------------------------------------------------------------------#

def upcoming_shows(objectID, object="venue"):
  if object=="venue":
    all_shows = Show.query.filter_by(venue_id = objectID).all()
  elif object=="artist":
    all_shows = Show.query.filter_by(artist_id = objectID).all()
  else:
    raise ValueError("object must be venue or artist")
  current_time = datetime.now()
  counter = 0
  for show in all_shows:
    if show.time > current_time:
      counter += 1
  return counter

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues_by_location = {}

  venues = Venue.query.all()
  for venue in venues:
    venue_dict = {}
    venue_dict["id"] = venue.id
    venue_dict["name"] = venue.name
    venue_dict["num_upcoming_shows"] = upcoming_shows(venue.id)
    # add venue to the location dictionary of venues
    location = (venue.city, venue.state)
    try:
      venues_by_location[location].append(venue_dict)
    except KeyError:
      venues_by_location[location] = [venue_dict]
  
  data = []

  for location in venues_by_location:
    loc_dict = {}
    loc_dict["city"] = location[0]
    loc_dict["state"] = location[1]
    loc_dict["venues"] = venues_by_location[location]
    data.append(loc_dict)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }

  search_term=request.form.get('search_term', '')

  all_venues = Venue.query.all()
  matches = []
  for venue in all_venues:
    if search_term.upper() in venue.name.upper():
      match = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": upcoming_shows(venue.id)
      }
      matches.append(match)
  
  response = {}
  response["count"] = len(matches)
  response["data"] = matches

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link
  }
  if venue.seeking_talent == True:
    data["seeking_description"] = venue.seeking_talent_message
  
  # bucket associated shows
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now()
  all_shows = Show.query.filter_by(venue_id = venue_id).all()
  for show in all_shows:
    show_dict = {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.time
    }
    if show.time > current_time:
      upcoming_shows.append(show_dict)
    else:
      past_shows.append(show_dict)
  
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(past_shows)
  data["upcoming_shows_count"] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  # surface form validation errrors
  if not form.validate():
    flash("Please correct the following errors: " + str(form.errors))
    return render_template('forms/new_venue.html', form=form)
  else:
    # check for existing venue with the same name in the same city
    duplicate_venues = Venue.query.filter_by(name = form.data["name"], city = form.data["city"], state = form.data["state"]).all()
    if len(duplicate_venues) > 0:
      flash("Venue " + form.data["name"] + " in " + form.data["city"] + " already exists.")
      return render_template('forms/new_venue.html', form=form)
    # prepare and execute db write
    try:
      # clean up and augment field values
      field_values = dict(form.data)
      del field_values["csrf_token"]
      if field_values["seeking_talent_message"] != "":
        field_values["seeking_talent"] = True
      # try and persist the form submission in the database
      venue = Venue(**field_values)
      ##test_other = field_value["genres"]
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + form.data["name"] + ' was successfully listed!')
    except():
      db.session.rollback()
      flash('An error occurred. Venue ' + form.data["name"] + ' could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # not used in this application
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  all_artists = Artist.query.all()
  data = []
  for artist in all_artists:
    data.append({"id": artist.id, "name": artist.name})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')

  all_artists = Artist.query.all()
  matches = []
  for artist in all_artists:
    if search_term.upper() in artist.name.upper():
      match = {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": upcoming_shows(artist.id, object="artist")
      }
      matches.append(match)
  
  response = {}
  response["count"] = len(matches)
  response["data"] = matches

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link
  }
  if artist.seeking_venue == True:
    data["seeking_description"] = artist.seeking_venue_message
  
  # bucket associated shows in past vs upcoming
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now()
  all_shows = Show.query.filter_by(artist_id = artist_id).all()
  for show in all_shows:
    show_dict = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.time
    }
    if show.time > current_time:
      upcoming_shows.append(show_dict)
    else:
      past_shows.append(show_dict)
  
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(past_shows)
  data["upcoming_shows_count"] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # not implemented / not used in this application
  return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # not implemented / not used in this application
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # not implemented / not used in this application
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # not implemented / not used in this application
  return render_template('pages/home.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  # surface form validation errrors
  if not form.validate():
    flash("Please correct the following errors: " + str(form.errors))
    return render_template('forms/new_artist.html', form=form)
  else:
    # check for existing artist with the same name in the same city
    duplicate_artists = Artist.query.filter_by(name = form.data["name"], city = form.data["city"], state = form.data["state"]).all()
    if len(duplicate_artists) > 0:
      flash("An artist named " + form.data["name"] + " already exists in " + form.data["city"] + ".")
      return render_template('forms/new_artist.html', form=form)
    # prepare and execute db write
    try:
      # clean up and augment field values
      field_values = dict(form.data)
      del field_values["csrf_token"]
      if field_values["seeking_venue_message"] != "":
        field_values["seeking_venue"] = True
      # try and persist the form submission in the database
      artist = Artist(**field_values)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + form.data['name'] + ' was successfully listed!')
    except():
      db.session.rollback()
      flash('An error occurred. Artist ' + form.data['name'] + ' could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  all_shows = Show.query.all()
  data = []
  for show in all_shows:
    show_dict = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.time
    }
    data.append(show_dict)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  # surface form field validation errors
  if not form.validate():
    flash("Please correct the following errors: " + str(form.errors))
    if "start_time" in form.errors:
      flash("Please format start time as YYYY:MM:DD HH:MM")
    flash('Show could not be listed.')
    return render_template('forms/new_show.html', form=form)
  else:
    # try and look up IDs, collect any errors, surface them jointly
    error = False
    try:
      artist = Artist.query.get(form.data["artist_id"])
      assert len(artist.name) > 0
    except:
      error = True
      flash("Please provide a valid Artist ID.")
    try:
      venue = Venue.query.get(form.data["venue_id"])
      assert len(venue.name) > 0
    except:
      error = True
      flash("Please provide a valid Venue ID.")    
    if error == True:
      flash('Show could not be listed.')
      return render_template('forms/new_show.html', form=form)
    else:
      # try and write show to DB
      try:
        show = Show(venue_id = form.data["venue_id"], artist_id = form.data["artist_id"], time = form.data["start_time"])
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
      except():
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
      finally:
        db.session.close()
      return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
