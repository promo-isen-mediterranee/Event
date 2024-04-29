from app import db, app
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Person {self.first_name}>'

    def serialize(self):
        return {
            'id': self.id,
            'last_name': self.last_name,
            'first_name': self.first_name
        }


@app.route('/person')
def get_person_data():
    person_list = Person.query.all()
    serialized_persons = [person.serialize() for person in person_list]
    return serialized_persons


@app.route('/person/<uuid:id>/')
def person(id):
    person = Person.query.get_or_404(id)
    return person.serialize()
