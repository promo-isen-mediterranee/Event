from sqlalchemy.dialects.postgresql import UUID
from app import db, app, make_response, jsonify
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
    r_user_history = db.relationship(Users, backref="users_history", cascade="save-update")

    def __repr__(self):
        return f'<Event_status_history {self.set_on}>'

    def json(self):
        return {
            'id': self.id,
            'status_id': self.status_id,
            'event_id': self.event_id,
            'set_on': self.set_on,
            'set_by': self.set_by,
        }


@app.route('/events_status_history')
def get_event_history_data():
    try:
        history_list = Event_status_history.query.all()
        return make_response(jsonify([event.json() for event in history_list]), 200)
    except:
        return make_response(jsonify({'message': 'error getting history'}), 500)


@app.route('/events_status_history/<int:id>/')
def event_history(id):
    event_status_history = Event_status_history.query.get_or_404(id)
    return event_status_history.json()
