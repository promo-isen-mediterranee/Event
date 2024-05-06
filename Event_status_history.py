from sqlalchemy.dialects.postgresql import UUID
from app import db, app
from Event_status import Event_status
from Event import Event
from Users import Users
from werkzeug.exceptions import NotFound


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


@app.route('/event/history/<int:event_id>/')
def get_event_history(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        event_status_history = Event_status_history.query.filter_by(event_id=event_id).all()
        return [event.json(), [history.json() for history in event_status_history]]
    except NotFound as e:
        return f'Aucun evenement trouvé, {e}', 404
    except Exception as e:
        return f'Error getting items location using item id, {e}', 500
