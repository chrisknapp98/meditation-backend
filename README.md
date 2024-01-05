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

### start solution using script

On Linux machines, the `start_solution.sh` script can be used for deployment. 
By executing `./integration/start_solution.sh`, the current version of the repository is pulled, a .env file with 
default parameters is created, and the Docker containers are started.


## stop containers

`docker compose down`

## rebuild server image

After editing the `server.py` script it's necessary to rebuild its docker image:

`docker compose up -d --build --wait`

## Continuous Deployment

With each push containing relevant changes for the backend, the backend is redeployed on the public VServer. 
This is implemented in the file `.github/workflows/deploy_solution.yml`. When the CI/CD pipeline is executed, an 
SSH connection is established to the VServer, and the [deployment script](#start-solution-using-script) is executed. 