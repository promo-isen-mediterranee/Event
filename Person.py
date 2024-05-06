from app import db
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
    

def get_manager_id(last_name, first_name):
    manager = Person.query.filter_by(last_name=last_name, first_name=first_name).first()
    if manager is None:
        new_manager = Person(last_name=last_name, first_name=first_name)
        db.session.add(new_manager)
        db.session.commit()
        return new_manager.id
    else:
        return manager.id