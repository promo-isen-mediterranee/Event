from app import db
from sqlalchemy.sql.expression import func

class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f'<Location {self.city}>'

    def json(self):
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
            'room': self.room,
        }


def get_location_id(address, city, room):
    loc = Location.query.filter_by(address=address, city=city, room=room).first()
    if loc is None:
        new_loc = Location(id=db.session.query(func.max(Location.id) + 1), address=address, city=city, room=room)
        db.session.add(new_loc)
        db.session.commit()
        return new_loc.id
    else:
        return loc.id
