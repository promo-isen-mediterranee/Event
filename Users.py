from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    email = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def json(self):
        return {
            'id': self.id,
            'email': self.email,
        }
