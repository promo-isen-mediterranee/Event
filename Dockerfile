FROM python:3.12


###############################
#  Variables d'environnement  #
###############################

# Base de donnée
ENV DB_HOST=logistisen_db
ENV DB_PORT=5432
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV DB_NAME=logistisen_db
ENV SQLALCHEMY_TRACK_MODIFICATIONS=False

# Flask
ENV FLASK_APP=/API_Event/src/__init__.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV SESSION_DURATION_SECONDS=900


###############################
#  Configuration de l'image   #
###############################

# Création du répertoire de travail
WORKDIR /API_Event

# Copie des fichiers de configuration
COPY requirements.txt .

COPY ./pyproject.toml ./pyproject.toml

# Copie du code
COPY ./src ./src

COPY ./README.md ./README.md

# Installation des dépendances
#RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -e .

# Expose le port 5000
EXPOSE 5000

# Spécifie la commande à exécuter
#CMD ["flask", "run"]
CMD ["waitress-serve", "--port", "5000", "src:app"]