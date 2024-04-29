from app import db, app


class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f'<Location {self.city}>'

    def serialize(self):
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
            'room': self.room,
        }


@app.route('/location')
def get_location_data():
    location_list = Location.query.all()
    serialized_events = [location.serialize() for location in location_list]
    return serialized_events


@app.route('/location/<uuid:id>/')
def location(id):
    location = Location.query.get_or_404(id)
    return location.serialize()
