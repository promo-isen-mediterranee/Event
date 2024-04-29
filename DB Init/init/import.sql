-- Item, Location, ItemLocation
CREATE TABLE IF NOT EXISTS item (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS location (
    id SERIAL PRIMARY KEY,
    address VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    room VARCHAR(10),
    UNIQUE(address, city, room)
);

CREATE TABLE IF NOT EXISTS item_location (
    item_id INT REFERENCES item(id) ON UPDATE CASCADE ON DELETE CASCADE,
    location_id INT REFERENCES location(id) ON UPDATE CASCADE,
    quantity INT NOT NULL,
    CONSTRAINT item_location_pkey PRIMARY KEY (item_id, location_id)
);

-- User and Role
CREATE TABLE IF NOT EXISTS users (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    label VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_role (
    user_id uuid REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    role_id INT REFERENCES role(id) ON UPDATE CASCADE,
    CONSTRAINT user_role_pkey PRIMARY KEY (user_id, role_id)
);

-- Event, EventStatus and Person
CREATE TABLE IF NOT EXISTS event_status (
    id SERIAL PRIMARY KEY,
    label VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS person (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS event (
    id SERIAL PRIMARY KEY,
    name VARCHAR(265) NOT NULL,
    stand_size INT NOT NULL,
    contact_objective INT NOT NULL,
    date_event DATE NOT NULL,
    status_id INT REFERENCES event_status(id) ON UPDATE CASCADE,
    location_id INT REFERENCES location(id) ON UPDATE CASCADE,
    item_manager uuid REFERENCES person(id) ON UPDATE CASCADE,
    UNIQUE(name, date_event, location_id)
);

CREATE TABLE IF NOT EXISTS event_status_history (
    id SERIAL PRIMARY KEY,
    set_on TIMESTAMP NOT NULL,
    event_id INT REFERENCES event(id) ON UPDATE CASCADE ON DELETE CASCADE,
    status_id INT REFERENCES event_status(id) ON UPDATE CASCADE,
    set_by uuid REFERENCES users(id) ON UPDATE CASCADE
);

-- Reserved item
CREATE TABLE IF NOT EXISTS reserved_item (
    item_id INT REFERENCES item(id) ON UPDATE CASCADE ON DELETE CASCADE,
    event_id INT REFERENCES event(id) ON UPDATE CASCADE ON DELETE CASCADE,
    quantity INT NOT NULL,
    status BOOLEAN NOT NULL,
    reserved_on DATE NOT NULL,
    reserved_by uuid REFERENCES users(id) ON UPDATE CASCADE,
    CONSTRAINT reserved_item_pkey PRIMARY KEY (item_id, event_id)
);

-- Alert and emails
CREATE TABLE IF NOT EXISTS alert (
    id SERIAL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS alert_email (
    email VARCHAR(30) PRIMARY KEY,
    alert_id INT REFERENCES alert(id) ON UPDATE CASCADE ON DELETE CASCADE
);

set timezone='Europe/Paris';

INSERT INTO location (address, city, room) VALUES ('Palais Neptune', 'Toulon', '007');
INSERT INTO location (address, city, room) VALUES ('Palais Neptune', 'Marseille', '013');
INSERT INTO users(email) VALUES ('marc.etavard@isen.yncrea.fr');
INSERT INTO users(email) VALUES('alex.olivier@isen.yncrea.fr');
INSERT INTO person(last_name, first_name) VALUES ('ETAVARD', 'Marc');
INSERT INTO person(last_name, first_name) VALUES ('OLIVIER', 'Alëx');
INSERT INTO event_status(label) VALUES ('A faire');
INSERT INTO event_status(label) VALUES ('Pret');
INSERT INTO event_status(label) VALUES ('Recupere');
INSERT INTO event_status(label) VALUES ('En attente de reception');
INSERT INTO event_status(label) VALUES ('Receptionne');
INSERT INTO event_status(label) VALUES ('Fini');

INSERT INTO event(name, stand_size, contact_objective, date_event, status_id, item_manager, location_id) 
VALUES('Salon étudiant Studyrama', 100, 50, TIMESTAMP '2024-2-8', 1,
       (SELECT id FROM person WHERE last_name = 'ETAVARD'),
       (SELECT id FROM location WHERE city = 'Toulon'));
INSERT INTO event(name, stand_size, contact_objective, date_event, status_id, item_manager, location_id) 
VALUES('Salon étudiant Studyrama', 150, 75, current_date, 1,
       (SELECT id FROM person WHERE last_name = 'OLIVIER'),
       (SELECT id FROM location WHERE city = 'Marseille'));