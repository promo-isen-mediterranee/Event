import uuid
from flask import current_app
from flask_login import current_user
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import func, text

db = current_app.db


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    username = db.Column(db.String(101), nullable=False)
    mail = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_authenticated = db.Column(db.Boolean, nullable=False, default=False)

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'mail': self.mail,
            'nom': self.nom,
            'prenom': self.prenom,
            'is_active': self.is_active
        }


class Roles(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    label = db.Column(db.String(20), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "label": self.label
        }


class User_role(db.Model):
    __tablename__ = "user_role"

    user_id = db.Column(db.UUID, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)

    r_user = db.relationship(Users, backref="users_role")
    r_role = db.relationship(Roles, backref="role")

    def json(self):
        return {
            "user": self.r_user.json(),
            "role": self.r_role.json()
        }


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name
        }


class Event_status(db.Model):
    __tablename__ = "event_status"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "label": self.label
        }


class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(10), nullable=True)

    def json(self):
        return {
            "id": self.id,
            "address": self.address,
            "city": self.city,
            "room": self.room
        }


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(265), nullable=False)
    stand_size = db.Column(db.Integer, nullable=True)
    contact_objective = db.Column(db.Integer, nullable=False, default=100)
    date_start = db.Column(db.DateTime(timezone=True), nullable=False)
    date_end = db.Column(db.DateTime(timezone=True), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    item_manager = db.Column(db.UUID, db.ForeignKey('person.id'))

    r_stat = db.relationship(Event_status, backref="event_status", cascade="save-update")
    r_loc = db.relationship(Location, backref="location", cascade="save-update")
    r_item_manager = db.relationship(Person, backref="person", cascade="save-update")

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'stand_size': self.stand_size,
            'contact_objective': self.contact_objective,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'status': self.r_stat.json(),
            'location': self.r_loc.json(),
            'item_manager': self.r_item_manager.json()
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
            "id": self.id,
            "status_id": self.status_id,
            "event_id": self.event_id,
            "set_on": self.set_on,
            "set_by": self.set_by,
        }


class Permissions(db.Model):
    __tablename__ = "permission"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    label = db.Column(db.String(20), nullable=False, unique=True)

    def json(self):
        return {
            "id": self.id,
            "label": self.label
        }


class Role_permissions(db.Model):
    __tablename__ = "role_permission"

    role_id = db.Column(db.Integer, db.ForeignKey('role.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', onupdate='CASCADE', ondelete='CASCADE'),
                              primary_key=True)

    r_role = db.relationship(Roles, backref="role_permissions")
    r_permission = db.relationship(Permissions, backref="permission")

    def json(self):
        return {
            "role": self.r_role.json(),
            "permission": self.r_permission.json()
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


def change_history(event):
    history = Event_status_history(
        status_id=event.status_id,
        event_id=event.id,
        set_on=func.now().op('AT TIME ZONE')(text("'Europe/Paris'")),
        set_by=current_user.id
    )
    db.session.add(history)
    db.session.commit()


def empty(str):
    return str == "" or str.isspace()
