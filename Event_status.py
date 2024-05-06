from app import db, app, make_response, jsonify


class Event_status(db.Model):
    __tablename__ = "event_status"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Event_status {self.label}>'

    def json(self):
        return {
            'id': self.id,
            'label': self.label,
        }
