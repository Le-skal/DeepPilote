# MLflow Server pour DeepPilot
# Hébergé sur Render avec SQLite comme backend (simple et gratuit)
#
# Build: docker build -t deeppilot-mlflow ./mlflow
# Run local: docker run -p 5000:5000 deeppilot-mlflow

FROM python:3.11-slim

# Metadata
LABEL maintainer="Raphael Martin"
LABEL description="MLflow tracking server for DeepPilot"

# Install dependencies (pas besoin de psycopg2 avec SQLite)
RUN pip install --no-cache-dir \
    mlflow==2.14.0 \
    boto3==1.34.0

# Create directories for SQLite DB and artifacts
RUN mkdir -p /data /mlruns
WORKDIR /app

# Expose MLflow default port
EXPOSE 5000

# Start MLflow server with SQLite backend
# Note: Les données sont stockées dans /data/mlflow.db
# Sur Render free tier, les données sont perdues au redémarrage (pas de disque persistant)
# Pour un projet étudiant c'est OK - les expériences sont aussi loggées localement
CMD ["mlflow", "server", \
    "--host", "0.0.0.0", \
    "--port", "5000", \
    "--backend-store-uri", "sqlite:///data/mlflow.db", \
    "--default-artifact-root", "/mlruns", \
    "--serve-artifacts"]
