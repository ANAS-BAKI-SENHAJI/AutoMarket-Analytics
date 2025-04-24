
#!/bin/bash

set -e

CONTAINER_NAME=projet_auto_db
SQL_FILE=init_db.sql

echo "📦 Copie de $SQL_FILE dans le container $CONTAINER_NAME..."
docker cp $SQL_FILE $CONTAINER_NAME:/tmp/$SQL_FILE

echo "🛠️  Exécution du script SQL dans la base 'airflow'..."
docker exec -i $CONTAINER_NAME psql -U postgres -d Projet_auto -f /tmp/$SQL_FILE
# docker exec -i $projet_auto_db psql -U postgres -d Projet_auto -f /tmp/init_db.sql

# docker exec -i projet-auto-etl-streamlit-main-airflow-postgres-1 psql -U airflow -d airflow -f /tmp/init_db.sql

echo "✅ Base de données initialisée avec succès !"
