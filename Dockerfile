# Base image : Python 3.10 avec peu de dépendances système
FROM python:3.10-slim

# Empêche Python de créer des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Affiche les logs Python immédiatement
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système nécessaires (pour psycopg2, numpy, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crée le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier requirements.txt dans l'image
COPY requirements.txt .

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le projet dans le conteneur
COPY . .

# Expose le port de Streamlit
EXPOSE 8501

# La commande réelle est dans le docker-compose.yml (streamlit run ...)

# Commande par défaut pour lancer Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]