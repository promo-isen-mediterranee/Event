from app import db, app, make_response, jsonify
from Location import Location
from Event_status import Event_status
from Person import Person
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.exceptions import NotFound


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(265), nullable=False)
    stand_size = db.Column(db.Integer, nullable=True)
    contact_objective = db.Column(db.Integer, nullable=False, default = 100)
    date_start = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    item_manager = db.Column(UUID, db.ForeignKey('person.id'))

    r_stat = db.relationship(Event_status, backref="event_status", cascade="save-update")
    r_loc = db.relationship(Location, backref="location", cascade="save-update")
    r_item_manager = db.relationship(Person, backref="person", cascade="save-update")

    def __repr__(self):
        return f'<Event {self.name}>'

    def json(self):
        loc = Location.query.filter_by(id=self.location_id).first()
        person = Person.query.filter_by(id=self.item_manager).first()
        return {
            'id': self.id,
            'name': self.name,
            'stand_size': self.stand_size,
            'contact_objective': self.contact_objective,
            'date_start': self.date_start.strftime('%Y-%m-%d'),
            'date_end': self.date_end.strftime('%Y-%m-%d'),
            'status': {"id": Event_status.query.filter_by(id=self.status_id).first().id,
                       "label": Event_status.query.filter_by(id=self.status_id).first().label},
            'item_manager': {'id': person.id,
                             'name': person.last_name,
                             'surname': person.first_name},
            'location': {'id': loc.id,
                         'address': loc.address,
                         'city': loc.city,
                         'room': loc.room}
        }


@app.route('/event')
def get_event_data():
    try:
        event_list = Event.query.all()
        return make_response(jsonify([event.json() for event in event_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting events, {e}'}), 500)


@app.route('/event/<int:id>/')
def event(id):
    event = Event.query.get_or_404(id)
    return event.json()


@app.route('/event/<string:event_status>')
def get_events_by_status(event_status):
    try:
        status_id = Event_status.query.filter_by(label=event_status).first().id
        event_list = Event.query.filter_by(status_id=status_id).all()
        return make_response(jsonify([event.json() for event in event_list]), 200)
    # except Unauthorized as e:
    #     return make_response(jsonify({f'Utilisateur non authentifié, {e}'}), 401)
    except NotFound as e:
        return make_response(jsonify({f'Aucun evenement trouvé, {e}'}), 404)
    except KeyError as e:
        return make_response(jsonify({f'Le statut fourni est incorrect, {e}'}), 400)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting items location using item id, {e}'}), 500)
