 # install python requirements
 
`pip install -r requirements.txt`

# deployment using docker compose

To make the deployment easier docker compose can be used to start the MariaDB 
and flask server.

## start containers

- open directory `integration`
- create an `.env` file from `.env.template`
- start containers and wait until they are healthy:

`docker compose up -d --wait`

To view the logs from the rest-server container, the command `docker logs rest-server` can be used.

## stop containers

`docker compose down`

## rebuild server image

After editing the `server.py` script it's necessary to rebuild its docker image:

`docker compose up -d --build --wait`