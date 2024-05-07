from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import func, text


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    email = db.Column(db.String(30), nullable=False)


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    

class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(10), nullable=True)


class Event_status(db.Model):
    __tablename__ = "event_status"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)
    

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


class Event_status_history(db.Model):
    __tablename__ = "event_status_history"

    id = db.Column(db.Integer, primary_key=True)
    status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    set_on = db.Column(db.DateTime(timezone=True))
    set_by = db.Column(UUID, db.ForeignKey('users.id'))

    r_event_history = db.relationship(Event, backref="event_history", cascade="save-update, delete")
    r_stat_history = db.relationship(Event_status, backref="event_status_history", cascade="save-update")
    r_user_history = db.relationship(Users, backref="users_history", cascade="save-update")

    def json(self):
        return {
            'id': self.id,
            'status_id': self.status_id,
            'event_id': self.event_id,
            'set_on': self.set_on,
            'set_by': self.set_by,
        }

def get_status_id(label):
    status = Event_status.query.filter_by(label=label).first()
    return status.id


def get_manager_id(last_name, first_name):
    manager = Person.query.filter_by(last_name=last_name, first_name=first_name).first()
    if manager is None:
        new_manager = Person(last_name=last_name, first_name=first_name)
        db.session.add(new_manager)
        db.session.commit()
        return new_manager.id
    else:
        return manager.id


def get_location_id(address, city, room):
    loc = Location.query.filter_by(address=address, city=city, room=room).first()
    if loc is None:
        new_loc = Location(id=db.session.query(func.max(Location.id) + 1), address=address, city=city, room=room)
        db.session.add(new_loc)
        db.session.commit()
        return new_loc.id
    else:
        return loc.id


def change_history(event):
    history = Event_status_history(status_id=event.status_id,
                                   event_id=event.id,
                                   set_on=func.now().op('AT TIME ZONE')(text("'Europe/Paris'")),
                                   set_by=Users.query.filter_by(email="marc.etavard@isen.yncrea.fr").first().id
                                   # TODO -> current user
                                   )
    db.session.add(history)
    db.session.commit()