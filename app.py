#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from flask_migrate import Migrate
import re
# from wtforms.validators import StopValidation
from wtforms.validators import ValidationError



from flask_migrate import Migrate

from models import Venue, Artist, Show, app, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# app = Flask(__name__)
# moment = Moment(app)
# app.config.from_object('config')
# db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

def validatePhoneNumber(form):
    phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
    match = re.search(phone_num, form.phone.data)
    if not match:
      flash('Error Phone Number must be in format xxx-xxx-xxxx')
      raise ValidationError('Error: Phone Number must be in format xxx-xxx-xxxx')

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_shows = Show.query.join(Artist).join(Venue).filter(Show.artist_id == Artist.id).filter(Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).with_entities(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time).order_by(Show.id.desc()).limit(10).all()
  
  upcoming_shows_data = []
  
  for show in recent_shows:
    d = {}
    d['venue_id'] = show[Venue.id]
    d['venue_name'] = show[Venue.name]
    d['artist_id']  = show[Artist.id]
    d['artist_name'] = show[Artist.name]
    d['artist_image_link'] = show[Artist.image_link]
    d['start_time'] = str(show[Show.start_time])
    
    upcoming_shows_data.append(d)
  
  # print(recent_shows)
  
  # recent_venues = Venue.query.order_by(Venue.id.desc()).with_entities(Venue.city, Venue.state).group_by(Venue.state, Venue.city, Venue.id).limit(10).all()
  
  # recent_venue_data = []
  # for venue in recent_venues:
  #   d_venues = []
  #   ven_in_same_city_state = Venue.query.filter(Venue.state == venue.state, Venue.city == venue.city).all()
    
  #   for each in ven_in_same_city_state:
  #     num_of_upcoming_shows = Show.query.join(Venue).filter(Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).count()
  #     d_venues.append(
  #       {
  #         'id': each.id,
  #         'name': each.name,
  #         'num_of_upcoming_shows': num_of_upcoming_shows
  #       }
  #     )
      
  #   recent_venue_data.append({
  #     'city': venue.city,
  #     'state': venue.state,
  #     'venues': d_venues
  #   })
      
  return render_template('pages/home.html', shows=upcoming_shows_data)

#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():     
  venues = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.state, Venue.city).all()
  data = []
  for venue in venues:
    d_venues = []
    ven_in_same_city_state = Venue.query.filter(Venue.state == venue.state, Venue.city == venue.city).all()
    
    for each in ven_in_same_city_state:
      num_of_upcoming_shows = Show.query.join(Venue).filter(Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).count()
      d_venues.append(
        {
          'id': each.id,
          'name': each.name,
          'num_of_upcoming_shows': num_of_upcoming_shows
        }
      )
      
    data.append({
      'city': venue.city,
      'state': venue.state,
      'venues': d_venues
    })
    # data.append(d_venues)
    # print(data)
  # return data
  
  return render_template('pages/venues.html', areas=data)

  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_query = request.form.get('search_term')
  search_result = Venue.query.filter(Venue.name.ilike('%' + search_query + '%')).all()
  
  response = {}
  d = []
  for each in search_result:
    d.append(
      {
        'id': each.id,
        'name': each.name,
        'num_upcoming_shows': 0
      }
    )
  response["count"] = len(search_result)
  response["data"] = d
      
  # print(search_result)
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)
  p_shows = Venue.query.join(Show).filter(Venue.id == Show.venue_id).with_entities(Show.artist_id, Show.start_time).filter(Show.start_time < datetime.now()).all()
  
  upc_shows = Venue.query.join(Show).filter(Venue.id == Show.venue_id).with_entities(Show.artist_id, Show.start_time).filter(Show.start_time > datetime.now()).all()
  
  upcoming_shows = []
  for each in upc_shows:
    d = {}
    artist = Artist.query.get(each[0])
    d['artist_id'] = artist.id
    d['artist_name'] = artist.name
    d['artist_image_link'] = artist.image_link
    d['start_time'] = str(each[1])
    upcoming_shows.append(d)
    
  past_shows = []
  for each in p_shows:
    d = {}
    artist = Artist.query.get(each[0])
    d['artist_id'] = artist.id
    d['artist_name'] = artist.name
    d['artist_image_link'] = artist.image_link
    d['start_time'] = str(each[1])
    past_shows.append(d)

  # data = {}
  
  venue_info = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres.split(','),
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(p_shows),
    'upcoming_shows_count': len(upc_shows)
  }  
  # venues = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.state, Venue.city).all()
  
  data = venue_info
  
  # print(data)
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
      
  try:
    form = VenueForm(request.form)
    validatePhoneNumber(form)

    venue = Venue(name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  address=form.address.data,
                  phone=form.phone.data,
                  genres=','.join(form.genres.data),
                  facebook_link=form.facebook_link.data,
                  image_link=form.image_link.data,
                  website_link=form.website_link.data,
                  seeking_talent=form.seeking_talent.data,
                  description=form.seeking_description.data
                  )
    
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')

  except:
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')
  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    print(venue_id)
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/venues.html')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  # print(artists[0][1])
  data = []
  
  for artist in artists:
    d = {}
    d['id'] = artist.id
    d['name'] = artist.name
    data.append(d)
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_query = request.form.get('search_term')
  search_result = Artist.query.filter(Artist.name.ilike('%' + search_query + '%')).all()
  response = {}
    
  response['count'] = len(search_result)
  
  data = []
  
  for each in search_result:
    num_of_upc_shows = Artist.query.join(Show).filter(Artist.id == Show.artist_id).filter(Show.start_time > datetime.now()).count()
    d = {}
    d['id'] = each.id
    d['name'] = each.name
    d['num_upcoming_shows'] = num_of_upc_shows
    data.append(d)
  response['data'] = data
  
  # print(response)
  
  
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  
  p_shows = Artist.query.join(Show).filter(Artist.id == Show.artist_id).with_entities(Show.venue_id, Show.start_time).filter(Show.start_time < datetime.now()).all()
  
  upc_shows = Artist.query.join(Show).filter(Artist.id == Show.artist_id).with_entities(Show.venue_id, Show.start_time).filter(Show.start_time > datetime.now()).all()
  
  upcoming_shows = []
  for each in upc_shows:
    d = {}
    venue = Venue.query.get(each[0])
    d['venue_id'] = venue.id
    d['venue_name'] = venue.name
    d['venue_image_link'] = venue.image_link
    d['start_time'] = str(each[1])
    upcoming_shows.append(d)
    
  past_shows = []
  for each in p_shows:
    d = {}
    venue = Venue.query.get(each[0])
    d['venue_id'] = venue.id
    d['venue_name'] = venue.name
    d['venue_image_link'] = venue.image_link
    d['start_time'] = str(each[1])
    past_shows.append(d)
  
  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres.split(','),
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.looking_for_venues,
    'seeking_description': artist.description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(p_shows),
    'upcoming_shows_count': len(upc_shows)
  }  
  
  
  print(data)
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
 
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  artist = Artist.query.get(artist_id)  
  artist_id = artist.id
  form.name.data = artist.name
  form.genres.data = ','.join(artist.genres)
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_description.data = artist.description
  form.seeking_venue.data = artist.looking_for_venues
  
  # print(form.genres.data)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    
    form = ArtistForm(request.form)
    validatePhoneNumber(form)
    artist = Artist.query.get(artist_id)
    
    artist.name = form.name.data
    artist.genres = ", ".join(request.form.getlist('genres'))
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.website_link  = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.description = form.seeking_description.data
    artist.looking_for_venues = form.seeking_venue.data
    
    db.session.commit()
    
    flash('Artist ' + form.name.data + ' was successfully edited!')

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')
    # print(sys.exc_info())
    pass
  finally:
    db.session.close()  

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  venue = Venue.query.get(venue_id)
  
  
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_description.data = venue.description
  form.seeking_talent.data = venue.seeking_talent

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm(request.form)
    validatePhoneNumber(form)
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = ", ".join(request.form.getlist('genres'))
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.website_link  = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.description = form.seeking_description.data
    venue.seeking_talent = form.seeking_talent.data
    
    db.session.commit()
    
    flash('Venue ' + form.name.data + ' was successfully edited!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be edited.')
    # print(sys.exc_info())
    pass
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():  
  try:
    form = ArtistForm(request.form)
    validatePhoneNumber(form)
    artist = Artist(
      name=form.name.data,
      city =form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = ','.join(form.genres.data),
      facebook_link = form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      looking_for_venues=form.seeking_venue.data,
      description=form.seeking_description.data
      )
    
    db.session.add(artist)
    db.session.commit()
    flash('Venue ' + artist.name + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    # print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  shows = Show.query.join(Artist).join(Venue).filter(Show.artist_id == Artist.id).filter(Show.venue_id == Venue.id).with_entities(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time).all()
  
  data = []
  
  for show in shows:
    d = {}
    d['venue_id'] = show[Venue.id]
    d['venue_name'] = show[Venue.name]
    d['artist_id']  = show[Artist.id]
    d['artist_name'] = show[Artist.name]
    d['artist_image_link'] = show[Artist.image_link]
    d['start_time'] = str(show[Show.start_time])
    
    data.append(d)
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
