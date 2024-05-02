from app import db, app, make_response, jsonify
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Person {self.first_name}>'

    def json(self):
        return {
            'id': self.id,
            'last_name': self.last_name,
            'first_name': self.first_name
        }


@app.route('/person')
def get_person_data():
    try:
        person_list = Person.query.all()
        return make_response(jsonify([person.json() for person in person_list]), 200)
    except:
        return make_response(jsonify({'message': 'Error getting persons'}), 500)


@app.route('/person/<uuid:id>/')
def person(id):
    person = Person.query.get_or_404(id)
    return person.json()
