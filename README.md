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