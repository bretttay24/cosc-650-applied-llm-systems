FROM python:3.12-slim

# mlflow[genai] pulls in the GenAI extras: AI gateway, automatic evaluation,
# prompt optimization, and server-side token/cost computation for traces.
# psycopg2-binary is needed for the Postgres backend store.
RUN pip install --no-cache-dir \
    "mlflow[genai]==3.16.1" \
    "psycopg[binary]>=3.2,<4" \
    "psycopg2-binary==2.9.10"

EXPOSE 5000

CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
