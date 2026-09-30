# Local pgvector

This Compose stack provides a PostgreSQL 16 database with the `pgvector` extension for reusable RAG and vector-search projects. It is independent of the MLflow stack.

## Configuration

Edit `docker.env` and replace `change-me-before-start` with a local password before starting the container. Do not commit `docker.env`.

## Start

Run from the repository root:

```powershell
docker compose --env-file docker/pgvector/docker.env -f docker/pgvector/docker-compose.yml up -d
```

This command does not build a local image. It pulls `pgvector/pgvector:pg16` if the image is not already available.

## Connection

From the host machine:

```text
postgresql://rag:<your-password>@localhost:55433/rag
```

From another container on its own Compose network, use the host machine connection or attach both projects to a shared Docker network. The `postgres` service name is only resolvable inside this stack's default network.

## Verify

```powershell
docker compose --env-file docker/pgvector/docker.env -f docker/pgvector/docker-compose.yml ps
docker exec -it rag-postgres psql -U rag -d rag -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

The `init.sql` script runs only when PostgreSQL initializes a new `pgvector_data` volume. If the database was already initialized without the extension, run the `CREATE EXTENSION` statement manually.

## Stop

Stop the container while preserving data:

```powershell
docker compose --env-file docker/pgvector/docker.env -f docker/pgvector/docker-compose.yml down
```

To remove the database data as well, use `down -v`. This is destructive.
