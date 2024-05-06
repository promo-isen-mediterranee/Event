from app import db


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
    
def get_status_id(label):
    status = Event_status.query.filter_by(label=label).first()
    return status.id
