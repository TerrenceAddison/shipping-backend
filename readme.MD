# shipping-backend

Simple backend system of a shipping service to check for rates of shipping some goods, built using python and FastAPI
Rates are automatically imported (from data/rates (1).json) into the database when the system is run.
You can see the import function under `populate_db.py`.

## Setup

### Local

run `pip install requirements.txt` to install all required files to run locally.
check file `database.py`and make sure that the `DATABASE_URL` is set to the one for localhost.

### Docker

check file `database.py`and make sure that the `DATABASE_URL` is set to the one for docker.

## Running

### Local

run `uvicorn main:app` from root directory to run

### Docker

run `docker-compose up` for first time and if you need to rebuild run `docker-compose up -d --build`

## Test

### Local

Run `pytest` from root directory to run the test

### Docker

When you run the docker container, a test container will be created (test-1 in my case). check the terminal of that container to see if there are any errors.
