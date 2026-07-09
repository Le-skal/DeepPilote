# MLflow Server pour DeepPilot
# Hébergé sur Render avec Supabase PostgreSQL comme backend
#
# Build: docker build -t deeppilot-mlflow ./mlflow
# Run local: docker run -p 5000:5000 -e DATABASE_URL=... deeppilot-mlflow

FROM python:3.11-slim

# Metadata
LABEL maintainer="Raphael Martin"
LABEL description="MLflow tracking server for DeepPilot"

# Install dependencies
RUN pip install --no-cache-dir \
    mlflow==2.14.0 \
    psycopg2-binary==2.9.9 \
    boto3==1.34.0

# Create directory for artifacts (local storage)
RUN mkdir -p /mlruns
WORKDIR /app

# Expose MLflow default port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start MLflow server
# - backend-store-uri: PostgreSQL pour les métadonnées (runs, params, metrics)
# - default-artifact-root: Stockage local pour les artifacts (modèles, plots)
# Note: Pour la prod, on pourrait utiliser S3/GCS pour les artifacts
CMD ["sh", "-c", "mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri ${DATABASE_URL} \
    --default-artifact-root /mlruns \
    --serve-artifacts"]
