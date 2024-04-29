from app import db, app
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    email = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
        }


@app.route('/users')
def get_user_data():
    users_list = Users.query.all()
    serialized_users = [user.serialize() for user in users_list]
    return serialized_users


@app.route('/users/<int:id>/')
def user(id):
    user = Users.query.get_or_404(id)
    return user.serialize()
