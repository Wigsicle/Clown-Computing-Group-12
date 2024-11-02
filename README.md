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
2. Set your database credentials in the env file (don't worry its not synced)
If DB Container Access Port 3307 is taken, change it to another available port in your env 
3. Start the database instance with ```docker-compose up```, ensure you have Docker Engine running

### Run the Flask-Migrate Schema migration script
4. Initialise the migrations folder into your program, if you DO NOT have the migrations/ folder in your flask app directory
    ``` 
    flask db init 
    ```
    If you have an existing migrations folder, run ``` flask db stamp head ```
5. Update the migrations folder with the latest model changes and push the schema changes to your database
    ``` 
    flask db migrate -m "<migration message>"
    flask db upgrade 
    ```
Whenever the models.py file gets updated, step 5's two commands will need to be rerun to do a migration.

### Run the Database Dummy Data Insertion Script
6. Run insert_script.py to insert data into the 4 tables

### Changing Database Stuff 
Schema (Tables and Columns): Step 5
Data: Edit the csv file that matches the table and then re-run step 6.

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
