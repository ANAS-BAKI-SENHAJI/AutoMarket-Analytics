# 📦 Makefile pour automatiser le lancement du projet AutoScoop

# Variables
CONTAINER_NAME=projet_auto_db
SQL_FILE=init_db.sql

# Commande pour installer les dépendances Python
install-deps:
	pip install -r requirements.txt

# Commande pour démarrer uniquement la base de données Docker
start-db:
	docker-compose up -d db

# Commande pour initialiser la base de données (copier et exécuter le fichier SQL)
init-db:
	docker cp init/$(SQL_FILE) $(CONTAINER_NAME):/tmp/$(SQL_FILE)
	docker exec -i $(CONTAINER_NAME) psql -U postgres -d Projet_auto -f /tmp/$(SQL_FILE)

# Commande pour démarrer l'application Streamlit
start-app:
	streamlit run app.py

# Commande principale : tout faire d'un coup
setup: install-deps start-db init-db start-app

# Nettoyer les conteneurs (optionnel)
clean:
	docker-compose down
