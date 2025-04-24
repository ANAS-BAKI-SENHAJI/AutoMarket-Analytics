#!/bin/bash

# Initialise la base si ce n'est pas déjà fait
echo "Initialisation de la DB Airflow..."
airflow db init

# Crée un utilisateur si besoin (à exécuter une fois seulement ou à mettre sous condition)
echo "Création de l'utilisateur admin..."
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@admin.com \
  --password admin

# Lance le scheduler en arrière-plan
echo "Démarrage du scheduler..."
airflow scheduler &

# Lance le webserver avec moins de workers
echo "Démarrage du webserver..."
airflow webserver --workers 1


