from flask import render_template, request, redirect
from sqlalchemy.sql.expression import func, text

from app import db, app
from Event import Event
from Location import Location
from Event_status_history import Event_status_history
from Person import Person
from Users import Users
from Event_status import Event_status


@app.route('/create', methods=('GET', 'POST'))
def create_event():
    if request.method == 'POST':
        name = request.form['name']
        stand_size = int(request.form['stand_size'])
        contact_objective = int(request.form['contact_objective'])
        date_event = request.form['date_event']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        address = request.form['address']
        city = request.form['city']
        room = request.form['room']

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
                      status_id=1,  # toujours à faire lors de la création
                      item_manager=item_manager,
                      location_id=location)

        db.session.add(event)
        db.session.commit()

        return redirect('/')

    return render_template('create.html')


@app.route('/edit/<int:event_id>', methods=('GET', 'POST'))
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    location = Location.query.get_or_404(event.location_id)
    item_manager = Person.query.get_or_404(event.item_manager)
    status = Event_status.query.get_or_404(event.status_id)

    if request.method == 'POST':
        stand_size = int(request.form['stand_size'])
        contact_objective = int(request.form['contact_objective'])
        date_event = request.form['date_event']
        label = request.form['label']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        address = request.form['address']
        city = request.form['city']
        room = request.form['room']

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

        return redirect('/')

    return render_template('edit.html', event=event, location=location, item_manager=item_manager, status=status)


@app.route('/delete/<int:event_id>', methods=('GET', 'POST'))
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        db.session.delete(event)
        db.session.commit()
        return redirect('/')
    return render_template('delete.html', event=event)


def change_history(event):
    history = Event_status_history(status_id=event.status_id,
                                   event_id=event.id,
                                   set_on=func.now().op('AT TIME ZONE')(text("'Europe/Paris'")),
                                   set_by=Users.query.filter_by(email="marc.etavard@isen.yncrea.fr").first().id  # TODO -> current user
                                   )
    db.session.add(history)
    db.session.commit()


with app.app_context():
    db.create_all()
    app.run()
