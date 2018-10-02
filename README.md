# User Management Service for Jupyter
This repo contains a small web service that talks to a database to keep track of permissions to let the RIT Jupyter spawner know which resources a user has access to.


## Building

```bash
docker build -t jupyterhub-user-service .
```


## Running

```bash
docker run \
    -e DB_NAME="table_name" \
    -e DB_USER="database_username" \
    -e DB_PASSWORD="user_password" \
    -e JUPYTERHUB_API_URL="https://jupyterhub/hub/api/" \
    -e JUPYTERHUB_API_TOKEN="12345" \
    -e PORT="10102" \
    jupyterhub-user-service
```


