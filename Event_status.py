from app import db, app


class Event_status(db.Model):
    __tablename__ = "event_status"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Event_status {self.label}>'

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
        }


@app.route('/event_status')
def get_status_data():
    events_status_list = Event_status.query.all()
    serialized_events_status = [event_status.serialize() for event_status in events_status_list]
    return serialized_events_status


@app.route('/event_status/<int:id>/')
def status(id):
    event_status = Event_status.query.get_or_404(id)
    return event_status.serialize()
