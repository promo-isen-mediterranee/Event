from app import db, app
from flask import request
from models import Event, Event_status, Event_status_history, Location, get_manager_id, change_history, get_status_id, empty
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.sql.expression import func


@app.route('/event/location/getAll')
def get_locations():
    try:
        locations = Location.query.all()
        return [location.json() for location in locations]
    except Exception as e:
        return f'Erreur lors de la récupération des emplacements, {e}', 500


@app.route('/event/status/getAll')
def get_event_status():
    try:
        status = Event_status.query.all()
        return [stat.json() for stat in status]
    except Exception as e:
        return f'Erreur lors de la récupération des statuts, {e}', 500
    

@app.route('/event/getAll')
def get_events():
    try:
        events = Event.query.all()
        return [event.json() for event in events]
    except Exception as e:
        return f'Erreur lors de la récupération des évènements, {e}', 500


@app.route('/event/<int:eventId>/')
def get_event(eventId):
    try:
        event = Event.query.get_or_404(eventId)
        return event.json()
    # except Unauthorized as e:
    #     return f'Utilisateur non authentifié, {e}', 401
    except NotFound as e:
        return f'Aucun evenement trouvé, {e}', 404
    except KeyError as e:
        return f'L ID fourni est incorrect, {e}', 400
    except Exception as e:
        return f'Erreur lors de la récupération de l évènement, {e}', 500


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


@app.route('/event/history/<int:eventId>/')
def get_event_history(eventId):
    try:
        event = Event.query.get_or_404(eventId)
        event_status_history = Event_status_history.query.filter_by(event_id=eventId).all()
        return [event.json(), [history.json() for history in event_status_history]]
    except NotFound as e:
        return f'Aucun evenement trouvé, {e}', 404
    except Exception as e:
        return f'Error getting items location using item id, {e}', 500
    


@app.route('/event/create', methods=['POST'])
def create_event():
    # try:
        request_form = request.form
        name = request_form['name']
        stand_size=0 if 'stand_size' not in request_form else int(request_form['stand_size'])
        # valeur par défaut si contact_objective pas spécifié : 100
        contact_objective=100 if 'contact_objective' not in request_form else int(request_form['contact_objective'])
        date_start = request_form['date_start']
        date_end = request_form['date_end']

        if 'item_manager.first_name' in request_form and 'item_manager.last_name' in request_form:
            last_name = request_form['item_manager.last_name']
            first_name = request_form['item_manager.first_name']
        else:
            last_name='A'
            first_name='Definir'
        if 'status.label' in request_form:
            label = request_form['status.label']
        else:
            label = 'A faire'

        if empty(name) or empty(date_start) or empty(date_end):
            return 'Erreur lors de la création d évènement, informations manquantes ou erronées', 400

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
    # except Exception as e:
    #     return f'Erreur lors de la création de l evenement : {e}', 500


@app.route('/event/<int:eventId>/', methods=['PUT'])
def update_event(eventId):
    try:
        event = Event.query.get_or_404(eventId)
        prev_status = Event_status.query.get_or_404(event.status_id)
        if event:
            request_form = request.form
            name = request_form['name']
            date_start = request_form['date_start']
            date_end = request_form['date_end']

            if empty(name) or empty(date_start) or empty(date_end):
                return 'Erreur lors de la mise à jour d évènement, informations erronées', 400
            event.name = name
            event.date_start = date_start
            event.date_end = date_end

            if 'stand_size' in request_form:
                event.stand_size = int(request_form['stand_size'])
            if 'contact_objective' in request_form:
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
            return 'Evenement mis à jour', 201
        
    except NotFound as e:    
        return 'Evenement à mettre à jour introuvable', 404
    # except Unauthorized as e:
    #     return ({f'Utilisateur non authentifié, {e}'}), 401)
    except BadRequest as e:
        return f'La requête est incomplète, {e} manquant', 400
    except Exception as e:
        return f'Erreur mise à jour de l évènement, {e} manquant', 500


@app.route('/event/<int:eventId>/', methods=['DELETE'])
def delete_event(eventId):
    try:
        event = Event.query.get_or_404(eventId)
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
        return f'Erreur suppression event, {e}', 500

