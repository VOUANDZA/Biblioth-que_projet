# 1️⃣ Utiliser une image Python 3.11
FROM python:3.11

# 2️⃣ Définir le répertoire de travail dans le conteneur
WORKDIR /app

# 3️⃣ Copier les fichiers de l’application dans le conteneur
COPY . .
ENV DISPLAY=host.docker.internal:0.0
# 4️⃣ Créer un environnement virtuel et installer les dépendances
RUN python -m venv venv && \
    venv/bin/pip install --no-cache-dir -r requirements.txt

# 5️⃣ Exposer le port (si l’application utilise un serveur)
EXPOSE 5000

# 6️⃣ Définir la commande pour exécuter l’application
CMD ["bash", "-c", "source venv/bin/activate && python main.py"]