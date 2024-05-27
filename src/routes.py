from datetime import timedelta
from functools import wraps
from os import environ
from flask import request, current_app, abort, session
from flask_login import current_user
from sqlalchemy.sql.expression import func
from src import login_manager, logger
from src.database import get_db
from src.models import Event, Event_status, Event_status_history, Location, Person, get_manager_id, change_history, \
    get_status_id, empty, User_role, Role_permissions, Users

db = get_db()


def response(obj=None, message=None, status_code=200):
    dictionary = {}

    if status_code >= 400:
        dictionary["error"] = message
    else:
        if obj is not None:
            dictionary = obj
        elif message is not None:
            dictionary["message"] = message

    return dictionary, status_code


def permissions_required(*permissions):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()

            if not permissions:
                return fn(*args, **kwargs)

            user_roles = User_role.query.filter_by(user_id=current_user.id).all()
            roles = [user_role.r_role for user_role in user_roles]
            has_permission = any(
                Role_permissions.query.filter_by(role_id=role.id, permission_id=permission).first()
                for role in roles for permission in permissions
            )

            if has_permission:
                return fn(*args, **kwargs)
            return abort(403)

        return decorated_view

    return wrapper


@current_app.before_request
def make_session_permanent():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(seconds=float(environ.get('SESSION_DURATION_SECONDS')))


@login_manager.user_loader
def user_loader(userId):
    return Users.query.get(userId)


@current_app.errorhandler(400)
def bad_request(e):
    logger.exception(f'Error occurred')
    return response(message='Requête incorrecte', status_code=400)


@current_app.errorhandler(401)
def unauthorized(e):
    logger.exception(f'Error occurred')
    return response(message='Non autorisé', status_code=401)


@current_app.errorhandler(403)
def forbidden(e):
    logger.exception(f'Error occurred')
    return response(message='Accès interdit', status_code=403)


@current_app.errorhandler(404)
def page_not_found(e):
    logger.exception(f'Error occurred')
    return response(message='Resource introuvable', status_code=404)


@current_app.errorhandler(405)
def method_not_allowed(e):
    logger.exception(f'Error occurred')
    return response(message='Méthode non autorisée', status_code=405)


@current_app.errorhandler(409)
def conflict(e):
    logger.exception(f'Error occurred')
    return response(message='Conflit', status_code=409)


@current_app.errorhandler(429)
def too_many_requests(e):
    logger.exception(f'Error occurred')
    return response(message=e, status_code=429)


@current_app.errorhandler(500)
def internal_server_error(e):
    logger.exception(f'Error occurred')
    return response(message='Erreur interne du serveur', status_code=500)


@current_app.get('/event/person/getAll')
@permissions_required(19)
def get_persons():
    persons = Person.query.all()
    return response(obj=[person.json() for person in persons])


@current_app.get('/event/location/getAll')
@permissions_required(7)
def get_locations():
    locations = Location.query.all()
    return response(obj=[location.json() for location in locations])


@current_app.get('/event/status/getAll')
@permissions_required(3)
def get_event_status():
    status = Event_status.query.all()
    return response(obj=[stat.json() for stat in status])


@current_app.get('/event/getAll')
@permissions_required(1)
def get_events():
    events = Event.query.all()
    return response(obj=[event.json() for event in events])


@current_app.get('/event/<int:eventId>')
@permissions_required(1)
def get_event(eventId):
    event = Event.query.get_or_404(eventId)
    return response(obj=event.json())


@current_app.get('/event/<string:event_status>')
@permissions_required(1)
def get_events_by_status(event_status):
    status_id = Event_status.query.filter_by(label=event_status).first().id
    event_list = Event.query.filter_by(status_id=status_id).all()
    return response(obj=[event.json() for event in event_list])


@current_app.get('/event/history/<int:eventId>')
@permissions_required(4)
def get_event_history(eventId):
    event = Event.query.get_or_404(eventId)
    event_status_history = Event_status_history.query.filter_by(event_id=eventId).all()
    return response(obj=[event.json(), [history.json() for history in event_status_history]])


@current_app.post('/event/create')
@permissions_required(2)
def create_event():
    request_form = request.form
    name = request_form['name']
    stand_size = 0 if empty(request_form["stand_size"]) else int(request_form['stand_size'])
    # valeur par défaut si contact_objective pas spécifié : 100
    contact_objective = 100 if empty(request_form["contact_objective"]) else int(request_form['contact_objective'])
    date_start = request_form['date_start']
    date_end = request_form['date_end']

    if 'item_manager.first_name' in request_form and 'item_manager.last_name' in request_form:
        last_name = request_form['item_manager.last_name']
        first_name = request_form['item_manager.first_name']
    else:
        last_name = 'A'
        first_name = 'Definir'
    if 'status.label' in request_form:
        label = request_form['status.label']
    else:
        label = 'A faire'

    if empty(name) or empty(date_start) or empty(date_end):
        abort(400)

    item_manager = get_manager_id(last_name, first_name)
    location_id = request_form["location.id"]
    status_id = get_status_id(label)

    new_id = db.session.query(func.max(Event.id) + 1).first()[0]

    event = Event(id=new_id,
                  name=name,
                  stand_size=stand_size,
                  contact_objective=contact_objective,
                  date_start=date_start,
                  date_end=date_end,
                  status_id=status_id,
                  item_manager=item_manager,
                  location_id=location_id)

    db.session.add(event)
    db.session.commit()

    return response(message='Event created', status_code=201)


@current_app.put('/event/<int:eventId>')
@permissions_required(2)
def update_event(eventId):
    event = Event.query.get_or_404(eventId)
    prev_status = Event_status.query.get_or_404(event.status_id)
    if event:
        request_form = request.form
        name = request_form['name']
        date_start = request_form['date_start']
        date_end = request_form['date_end']

        if empty(name) or empty(date_start) or empty(date_end):
            abort(400)
        event.name = name
        event.date_start = date_start
        event.date_end = date_end

        if not empty(request_form['stand_size']):
            event.stand_size = int(request_form['stand_size'])
        if not empty(request_form['contact_objective']):
            event.contact_objective = int(request_form['contact_objective'])
        if 'status.label' in request_form:
            label = request_form['status.label']
            new_status = Event_status.query.filter_by(label=label).first()
            event.status_id = new_status.id
            if prev_status.label != label:
                change_history(event)  # changement status -> event_status_history stocke le nouveau

        if 'item_manager.first_name' in request_form and 'item_manager.last_name' in request_form:
            last_name = request_form['item_manager.last_name']
            first_name = request_form['item_manager.first_name']
            event.item_manager = get_manager_id(last_name, first_name)

        event.location_id = request_form["location.id"]

        db.session.commit()
        return response(message='Evenement mis à jour', status_code=201)


@current_app.delete('/event/<int:eventId>')
@permissions_required(2)
def delete_event(eventId):
    event = Event.query.get_or_404(eventId)
    db.session.delete(event)
    db.session.commit()
    return response(message='Evenement supprimé', status_code=204)
