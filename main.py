from flask import request, jsonify, make_response
from sqlalchemy.sql.expression import func, text

from app import db, app
from Event import Event
from Location import Location
from Event_status_history import Event_status_history
from Person import Person
from Users import Users
from Event_status import Event_status



@app.route('/events/create', methods=['POST'])
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

        manager = Person.query.filter_by(last_name=last_name, first_name=first_name).first()
        if manager is None:  # si pas trouvé on l'ajoute dans la DB
            new_manager = Person(last_name=last_name, first_name=first_name)
            db.session.add(new_manager)
            db.session.commit()
            item_manager = new_manager.id
        else:
            item_manager = manager.id

        loc = Location.query.filter_by(address=address, city=city, room=room).first()
        if loc is None:
            new_loc = Location(id=db.session.query(func.max(Location.id) + 1), address=address, city=city, room=room)
            db.session.add(new_loc)
            db.session.commit()
            location = new_loc.id
        else:
            location = loc.id


        event = Event(id=db.session.query(func.max(Event.id) + 1),
                    name=name,
                    stand_size=stand_size,
                    contact_objective=contact_objective,
                    date_event=date_event,
                    status_id= Event_status.query.filter_by(label='A faire').first().id,
                    item_manager=item_manager,
                    location_id=location)

        db.session.add(event)
        db.session.commit()

        return make_response(jsonify({'message': 'Event created'}), 201)

    except:
        return make_response(jsonify({'message': 'Error creating event'}), 500)


@app.route('/events/update/<int:event_id>', methods=['PUT'])
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

            new_manager = Person.query.filter_by(last_name=last_name, first_name=first_name).first()
            if new_manager is None:
                new_manager = Person(last_name=last_name, first_name=first_name)
                db.session.add(new_manager)
                db.session.commit()
            event.item_manager = new_manager.id

            new_location = Location.query.filter_by(address=address, city=city, room=room).first()
            if new_location is None:
                new_location = Location(id=db.session.query(func.max(Location.id) + 1), address=address, city=city,
                                        room=room)
                db.session.add(new_location)
                db.session.commit()
            event.location_id = new_location.id

            db.session.commit()
            return make_response(jsonify({'message': 'Event updated'}), 200)
        
        return make_response(jsonify({'message': 'Event not found'}), 404)
    except:
        return make_response(jsonify({'message': 'Error updating event'}), 500)


@app.route('/events/delete/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        print(event)
        if event:
            db.session.delete(event)
            db.session.commit()
            return make_response(jsonify({'message': 'Event deleted'}), 200)

        return make_response(jsonify({'message': 'Event not found'}), 404)
    except:
        return make_response(jsonify({'message': 'Error deleting event'}), 500)


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
