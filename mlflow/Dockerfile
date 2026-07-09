# MLflow Server pour DeepPilot
# Hébergé sur Render avec SQLite comme backend (simple et gratuit)
#
# Build: docker build -t deeppilot-mlflow ./mlflow
# Run local: docker run -p 5000:5000 deeppilot-mlflow

FROM python:3.11-slim

# Metadata
LABEL maintainer="Raphael Martin"
LABEL description="MLflow tracking server for DeepPilot"

# Install dependencies
RUN pip install --no-cache-dir mlflow==2.14.0

# Create work directory with proper permissions
WORKDIR /mlflow
RUN mkdir -p /mlflow/db /mlflow/artifacts && chmod -R 777 /mlflow

# Expose MLflow default port
EXPOSE 5000

# Start MLflow server with SQLite backend (chemin absolu)
CMD ["mlflow", "server", \
    "--host", "0.0.0.0", \
    "--port", "5000", \
    "--backend-store-uri", "sqlite:////mlflow/db/mlflow.db", \
    "--default-artifact-root", "/mlflow/artifacts", \
    "--serve-artifacts"]
