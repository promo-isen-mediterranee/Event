from flask import request, jsonify, make_response
from sqlalchemy.sql.expression import func, text

from app import db, app
from Event import Event
from Location import get_location_id
from Event_status_history import Event_status_history
from Person import get_manager_id
from Users import Users
from Event_status import Event_status



@app.route('/events', methods=['POST'])
def create_event():
    try:
        request_form = request.get_json()

        name = request_form['name']
        stand_size = int(request_form['stand_size'])
        contact_objective = int(request_form['contact_objective'])
        date_event = request_form['date_event']
        last_name = request_form['last_name']
        first_name = request_form['first_name']
        address = request_form['address']
        city = request_form['city']
        room = request_form['room']

        last_name = last_name.upper()
        first_name = first_name[0].upper() + first_name[1:].lower()
        city = city[0].upper() + city[1:].lower()

        item_manager = get_manager_id(last_name, first_name)

        location_id = get_location_id(address, city, room)


        event = Event(id=db.session.query(func.max(Event.id) + 1),
                    name=name,
                    stand_size=stand_size,
                    contact_objective=contact_objective,
                    date_event=date_event,
                    status_id= Event_status.query.filter_by(label='A faire').first().id,
                    item_manager=item_manager,
                    location_id=location_id)

        db.session.add(event)
        db.session.commit()

        return make_response(jsonify({'message': 'Event created'}), 201)

    except Exception as e:
        return make_response(jsonify({'message': f'Error creating event, {e}'}), 500)


@app.route('/events/<int:event_id>/', methods=['PUT'])
def update_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        status = Event_status.query.get_or_404(event.status_id)
        if event:
            request_form = request.get_json()
            stand_size = int(request_form['stand_size'])
            contact_objective = int(request_form['contact_objective'])
            date_event = request_form['date_event']
            label = request_form['label']
            last_name = request_form['last_name']
            first_name = request_form['first_name']
            address = request_form['address']
            city = request_form['city']
            room = request_form['room']

            last_name = last_name.upper()
            first_name = first_name[0].upper() + first_name[1:].lower()
            city = city[0].upper() + city[1:].lower()

            event.stand_size = stand_size
            event.contact_objective = contact_objective
            event.date_event = date_event

            new_status = Event_status.query.filter_by(label=label).first()  # TODO menu deroulant avec les 6 status
            event.status_id = new_status.id

            if status.label != label:
                change_history(event)  # changement status -> event_status_history stocke le nouveau

            event.item_manager = get_manager_id(last_name, first_name)
            event.location_id = get_location_id(address, city, room)

            db.session.commit()
            return make_response(jsonify({'message': 'Event updated'}), 200)
        
        return make_response(jsonify({'message': 'Event not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating event, {e}'}), 500)


@app.route('/events/<int:event_id>/', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        if event:
            db.session.delete(event)
            db.session.commit()
            return make_response(jsonify({'message': 'Event deleted'}), 200)

        return make_response(jsonify({'message': 'Event not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting event, {e}'}), 500)


def change_history(event):
    history = Event_status_history(status_id=event.status_id,
                                   event_id=event.id,
                                   set_on=func.now().op('AT TIME ZONE')(text("'Europe/Paris'")),
                                   set_by=Users.query.filter_by(email="marc.etavard@isen.yncrea.fr").first().id
                                   # TODO -> current user
                                   )
    db.session.add(history)
    db.session.commit()


with app.app_context():
    db.create_all()
    app.run()
