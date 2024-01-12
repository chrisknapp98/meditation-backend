
# MindSync Backend

This project includes the backend for the [MindSync](https://github.com/marvpaul/flutter-meditation) meditation app. 
It consists of a REST server, a database, and an LSTMK machine learning model.

##  Table of contents
<!-- TOC -->
* [MindSync Backend](#mindsync-backend)
  * [Getting Started](#getting-started-)
    * [deployment using docker compose](#deployment-using-docker-compose)
      * [start containers](#start-containers)
      * [start solution using script](#start-solution-using-script)
      * [stop containers](#stop-containers)
      * [rebuild server image](#rebuild-server-image)
    * [deploy manually](#deploy-manually)
      * [1. Setup a MariaDB](#1-setup-a-mariadb)
      * [2. Install python dependencies](#2-install-python-dependencies)
      * [3. Set environment variables](#3-set-environment-variables)
      * [4. Run Flask server](#4-run-flask-server)
  * [Project structure](#project-structure)
  * [Testing](#testing)
    * [integration tests](#integration-tests)
      * [run tests](#run-tests)
        * [1. Deploy backend containers](#1-deploy-backend-containers)
        * [2. install test dependencies](#2-install-test-dependencies)
        * [3. Run integration tests](#3-run-integration-tests)
        * [4. Inspect test results](#4-inspect-test-results)
  * [CI/CD pipeline](#cicd-pipeline)
    * [Continuous Deployment](#continuous-deployment)
    * [Integration tests within CI/CD pipeline](#integration-tests-within-cicd-pipeline)
<!-- TOC -->

## Getting Started 

### deployment using docker compose

To make the deployment easier docker compose can be used to start the MariaDB 
and flask server.

#### start containers

- open directory `integration`
- create an `.env` file from `.env.template`
- start containers and wait until they are healthy:

`docker compose up -d --wait`

To view the logs from the rest-server container, the command `docker logs rest-server` can be used.

#### start solution using script

On Linux machines, the `start_solution.sh` script can be used for deployment. 
By executing `./integration/start_solution.sh`, the current version of the repository is pulled, a .env file with 
default parameters is created, and the Docker containers are started.

#### stop containers

`docker compose down`

#### rebuild server image

After editing the source code of the backend it's necessary to rebuild its docker image:

`docker compose up -d --build --wait`

### deploy manually

#### 1. Setup a MariaDB

#### 2. Install python dependencies

`pip install -r requirements.txt`

#### 3. Set environment variables

Create a `.env` file from `integration/.env.template` and set the correct variable values for your database. 
Make sure the .env file is located in the same directory as the execution directory from where you start the Flask 
server.

#### 4. Run Flask server

`python3 src/server.py`

## Project structure

![file structure](http://localhost:8080/svg/TLB1RiCW3Btp5TodmNQlfawRDFMwVK14Y9kY08vifrN_VYHKQQLbD-FtR3y_isTn9CSGWHKF8O-ENDAjyqDFEENk0oEI5dAP2mHPbBAc3tAQMdkFBaZ3CUA5RGTZn6l362S9cCqrnIrQo08zkPdI2B0iFBNBAF2clXQsVlSpp5hjRCshFsLiNr-Q15sGccDWdciCOOkonJyx2gujsvhnkeNJT8iCdrP1XpjDBw2-58dwUnvoB7x1lDW_Ecs7VW1wzfX6PAY6FE86yja8f34wWNNavrAbgvsf-FxOdidRo99i3SkXYghRewwnzld1YJneZnqiLuNSwISzvI1ratlNVO6MV_0B)


## Testing

### integration tests

In the backend, integration tests were written to test the REST interface. 
The tests were implemented using the Robot Framework and can be found in the 
`integration_tests` folder.

#### run tests

##### 1. Deploy backend containers
To execute the tests, it is necessary to [start the backend](#start-containers) beforehand using the docker compose setup.

##### 2. install test dependencies

Before the testsuite can be executed it's necessary to install the test dependencies:

`pip install -r requirements-test.txt`

##### 3. Run integration tests

If the tests are to be executed on a Linux system, they can be started by invoking the following script:

`./integration_tests/run_tests.sh`

Otherwise, the following commands must be executed:

```bash
cd integration_tests

python3 -m robot \
--variablefile variables.py \
--outputdir integration_test_results \
-L DEBUG \
-e PRIO2 \
.
```

##### 4. Inspect test results

After the tests have been executed, the results can be found in the `integration_tests/integration_test_results` folder.
There, you will find the test reports and logs.

## CI/CD pipeline

![activity diagram CI/CD pipeline](https://www.plantuml.com/plantuml/svg/VP2nRiCW68HtdkB6n4ltU6ZKTEcMeIz0pJd-5GA8_yUgtxx4xLpf1k3kFg4xg_bgxH6TYKNYyl5oUSTL2gCauirFTwRWzfGxNPiki8pAabKirsrqfyz555qv8N3khT2FJhco-eXXU89q64RdPCRXwvU8AGTYyOffyUd6y7g4BKmuRDIZ0qwr9KWotgetwMoZcevFfzIyIk3-WafjqHI-gqwBh1p_RxSIl1619URjmMJezYhLcezu-8v87S6en27b_Ijwbm9-iqqxAyyeVmFrO0eoEwUMYpltIv_o1m00)

### Continuous Deployment

With each push containing relevant changes for the backend, the backend is redeployed on the public VServer. 
This is implemented in the file `.github/workflows/deploy_solution.yml`. When the CI/CD pipeline is executed, an 
SSH connection is established to the VServer, and the [deployment script](#start-solution-using-script) is executed.

### Integration tests within CI/CD pipeline

With each commit, the tests are executed within a CI/CD pipeline of the repository. 
The test results can be downloaded as a zip archive from there. 
This ensures that the code consistently meets a certain quality standard, and changes do not break previously 
functional code.



