#!/bin/bash
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres

docker exec -it postgres bash -c "echo \"SELECT 'CREATE DATABASE ascii_converter' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ascii_converter')\gexec\" | psql -U postgres"

