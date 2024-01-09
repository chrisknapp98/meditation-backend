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

# integration tests

In the backend, integration tests were written to test the REST interface. 
The tests were implemented using the Robot Framework and can be found in the 
`integration_tests` folder.

## run tests

To execute the tests, it is necessary to [start the backend](#start-containers) beforehand using the docker compose setup.

Before the testsuite can be executed it's necessary to install the test dependencies:

`pip install -r requirements-test.txt`

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

## View test results

After the tests have been executed, the results can be found in the 'integration_tests/integration_test_results' folder.
There, you will find the test reports and logs.

## Integration tests within CI/CD pipeline

With each commit, the tests are executed within a CI/CD pipeline of the repository. 
The test results can be downloaded as a zip archive from there. 
This ensures that the code consistently meets a certain quality standard, and changes do not break previously 
functional code.

![activity diagram CI/CD pipeline](https://www.plantuml.com/plantuml/svg/VP2nRiCW68HtdkB6n4ltU6ZKTEcMeIz0pJd-5GA8_yUgtxx4xLpf1k3kFg4xg_bgxH6TYKNYyl5oUSTL2gCauirFTwRWzfGxNPiki8pAabKirsrqfyz555qv8N3khT2FJhco-eXXU89q64RdPCRXwvU8AGTYyOffyUd6y7g4BKmuRDIZ0qwr9KWotgetwMoZcevFfzIyIk3-WafjqHI-gqwBh1p_RxSIl1619URjmMJezYhLcezu-8v87S6en27b_Ijwbm9-iqqxAyyeVmFrO0eoEwUMYpltIv_o1m00)

