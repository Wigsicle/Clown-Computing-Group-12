# Project README

## Prerequisites

- Ensure you have Python interpreter installed. You can download and install Python from the official website: [python.org](https://www.python.org/downloads/).
- Docker (You will need to enable Virtualisation in your BIOS)

## Installation

Please install the following packages or libraries on requirements.txt
```
pip install -r requirements.txt
```

## Setting up Project Database
### Setting Your Local Development Environments
1. Create a .env file, following the variables in .env.example
2. Set your local database username and password credentials in the env file
(don't worry its not synced)
3. Create a local MariaDB instance of the 'ticket_hive' 

### Run the Flask-Migrate Schema migration script
4. Initialise the migrations folder into your program, only do this if you DO NOT have the migrations/ folder in your flask app directory
    ``` 
    flask db init 
    ```
5. Update the migrations folder with the latest model changes and push the schema changes to your database
    ``` 
    flask db migrate -m "<migration message>"
    flask db upgrade 
    ```
Whenever the models.py file gets updated, step 5's two commands will need to be rerun.
Sometimes, you may get a "target database out of date error". To fix this, run ``` flask db stamp head ``` then run step 5. 

### Run the Database Dummy Data Insertion Script
6. Run insert_script.py in dummy_insert folder

In the event that you need to change the data, just change the respective table csv files.

### Running the script ("OLD, MIGHT WORK, MAYBE." - DAN)
Once everything done, run the 'create_db.py' script to create the models, but you need to create a schema in your mysql host first "ticket_hive"

## Application Start Up
1. Start up the docker database container
    ```docker-compose up```
2. Start the Web Application by running app.py

You might face issues where you need to rebuild your container image after docker-compose changes, 
stop the container (if running) and then delete it.
```
docker stop <container_id>
docker rm <container_id> 
```
