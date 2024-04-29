from sqlalchemy.dialects.postgresql import UUID
from app import db, app
from Event_status import Event_status
from Event import Event
from Users import Users


class Event_status_history(db.Model):
    __tablename__ = "event_status_history"

    id = db.Column(db.Integer, primary_key=True)
    status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    set_on = db.Column(db.DateTime(timezone=True))
    set_by = db.Column(UUID, db.ForeignKey('users.id'))

    r_event_history = db.relationship(Event, backref="event_history", cascade="save-update, delete")
    r_stat_history = db.relationship(Event_status, backref="event_status_history", cascade="save-update")
    r_user_history = db.relationship(Users, backref="users", cascade="save-update")

    def __repr__(self):
        return f'<Event_status_history {self.set_on}>'

    def serialize(self):
        return {
            'id': self.id,
            'status_id': self.status_id,
            'event_id': self.event_id,
            'set_on': self.set_on,
            'set_by': self.set_by,
        }


@app.route('/event_status_history')
def get_event_history_data():
    events_status_history_list = Event_status_history.query.all()
    serialized_events_status_history = [event_status_history.serialize() for event_status_history in
                                        events_status_history_list]
    return serialized_events_status_history


@app.route('/event_status_history/<int:id>/')
def event_history(id):
    event_status_history = Event_status_history.query.get_or_404(id)
    return event_status_history.serialize()
