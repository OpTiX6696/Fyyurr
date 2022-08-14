
from enum import unique
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from forms import *
from flask_moment import Moment
from flask_migrate import Migrate



app = Flask(__name__)

moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True, nullable = False)
    name = db.Column(db.String(), nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False, unique = True)
    genres = db.Column(db.String(), nullable = False)
    website_link = db.Column(db.String(), nullable = True)
    image_link = db.Column(db.String(500), nullable = False)
    facebook_link = db.Column(db.String(120), nullable = True)
    seeking_talent = db.Column(db.Boolean, default = False, nullable = False)    
    description = db.Column(db.String(), nullable = True)
    show = db.relationship('Show', passive_deletes=True, backref = 'venue', lazy = True)
    
    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.genres} {self.website_link} {self.image_link} {self.facebook_link} {self.seeking_talent} {self.description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True, nullable = False)
    name = db.Column(db.String(), nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False, unique = True)
    genres = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500), nullable = False)
    facebook_link = db.Column(db.String(120), nullable = True)
    website_link = db.Column(db.String(), nullable = True)
    looking_for_venues = db.Column(db.Boolean, nullable = False, default = False)        
    description = db.Column(db.String(), nullable = True)
    show = db.relationship('Show', passive_deletes=True, backref = 'artist', lazy = True)
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.website_link} {self.image_link} {self.facebook_link} {self.looking_for_venues} {self.description}>'
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
class Show(db.Model):
  __tablename__ = 'show'
  
  id = db.Column(db.Integer, primary_key = True, nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), nullable = False)
  start_time = db.Column(db.DateTime(), nullable = False)
  
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


