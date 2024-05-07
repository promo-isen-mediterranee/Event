from app import db, app
from flask import request
from models import Event, Event_status, Event_status_history, get_manager_id, change_history, get_location_id, get_status_id
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.sql.expression import func


@app.route('/event')
def get_event_data():
    try:
        event_list = Event.query.all()
        return [event.json() for event in event_list], 200
    except Exception as e:
        return f'Error getting events, {e}', 500


@app.route('/event/<int:id>/')
def get_event(id):
    event = Event.query.get_or_404(id)
    return event.json()


@app.route('/event/<string:event_status>')
def get_events_by_status(event_status):
    try:
        status_id = Event_status.query.filter_by(label=event_status).first().id
        event_list = Event.query.filter_by(status_id=status_id).all()
        return [event.json() for event in event_list], 200
    # except Unauthorized as e:
    #     return f'Utilisateur non authentifié, {e}', 401
    except NotFound as e:
        return f'Aucun evenement trouvé, {e}', 404
    except KeyError as e:
        return f'Le statut fourni est incorrect, {e}', 400
    except Exception as e:
        return f'Error getting items location using item id, {e}', 500


@app.route('/event/history/<int:event_id>/')
def get_event_history(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        event_status_history = Event_status_history.query.filter_by(event_id=event_id).all()
        return [event.json(), [history.json() for history in event_status_history]]
    except NotFound as e:
        return f'Aucun evenement trouvé, {e}', 404
    except Exception as e:
        return f'Error getting items location using item id, {e}', 500
    


@app.route('/event/create', methods=['POST'])
def create_event():
    try:
        request_form = request.get_json()
        name = request_form['name']
        stand_size=0 if 'stand_size' not in request_form else int(request_form['stand_size'])
        # valeur par défaut si contact_objective pas spécifié : 100
        contact_objective=100 if 'contact_objective' not in request_form else int(request_form['contact_objective'])
        date_start = request_form['date_start']
        date_end = request_form['date_end']

        if 'item_manager' in request_form:
            item_manager = request_form['item_manager']
            last_name = item_manager['last_name']
            first_name = item_manager['first_name']
        else:
            last_name='A'
            first_name='Definir'

        if 'status' in request_form:
            status = request_form['status']
            label = status['label']
        else:
            label = 'A faire'

        location = request_form['location']
        address = location['address']
        city = location['city']
        room = '' if 'room' not in location else location['room']

        item_manager = get_manager_id(last_name, first_name)
        location_id = get_location_id(address, city, room)
        status_id = get_status_id(label)


        event = Event(id=db.session.query(func.max(Event.id) + 1),
                    name=name,
                    stand_size=stand_size,
                    contact_objective=contact_objective,
                    date_start=date_start,
                    date_end=date_end,
                    status_id= status_id,
                    item_manager=item_manager,
                    location_id=location_id)

        db.session.add(event)
        db.session.commit()

        return 'Event created', 201

    # except Unauthorized as e:
    #     return ({f'Utilisateur non authentifié, {e}'}), 401)
    # except Forbidden as e:
        # return ({f'Droits non suffisants, {e}'}), 403)
    # except KeyError:
    #     return ({f'La requête est incomplète'}), 400)
    except Exception as e:
        return f'Erreur lors de la création de l evenement : {e}', 500


@app.route('/event/<int:event_id>/', methods=['PUT'])
def update_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        prev_status = Event_status.query.get_or_404(event.status_id)
        if event:
            request_form = request.get_json()

            name = request_form['name']
            date_start = request_form['date_start']
            date_end = request_form['date_end']
            event.name = name
            event.date_start = date_start
            event.date_end = date_end

            if 'stand_size' in request_form:
                event.stand_size = int(request_form['stand_size'])
            if 'contact_objective' in request_form:
                event.contact_objective = int(request_form['contact_objective'])
            if 'status' in request_form:
                status = request_form['status']
                label = status['label']
                new_status = Event_status.query.filter_by(label=label).first()
                event.status_id = new_status.id
                print(prev_status.label, label)
                if prev_status.label != label:
                    change_history(event)  # changement status -> event_status_history stocke le nouveau
            
            if 'item_manager' in request_form:
                item_manager = request_form['item_manager']
                last_name = item_manager['last_name']
                first_name = item_manager['first_name']
                event.item_manager = get_manager_id(last_name, first_name)
            if 'location' in request_form:
                location = request_form['location']
                address = location['address']
                city = location['city']
                room = '' if 'room' not in location else location['room']
                event.location_id = get_location_id(address, city, room)

            db.session.commit()
            return 'Evenement mis à jour', 201
        
    except NotFound as e:    
        return 'Evenement à mettre à jour introuvable', 404
    # except Unauthorized as e:
    #     return ({f'Utilisateur non authentifié, {e}'}), 401)
    except BadRequest as e:
        return f'La requête est incomplète, {e} manquant', 400
    except Exception as e:
        return f'Erreur mise à jour de l évènement, {e} manquant', 500


@app.route('/event/<int:event_id>/', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        if event:
            db.session.delete(event)
            db.session.commit()
            return 'Evenement supprimé', 204

    except NotFound as e:
        return f'Evenement à supprimer introuvable, {e}', 404
    # except Unauthorized as e:
    #     return ({f'Utilisateur non authentifié, {e}'}), 401)    
    except BadRequest as e:
        return f'ID fourni incorrect, {e}', 400
    except Exception as e:
        return f'Error deleting event, {e}', 500
