# Project README

## Prerequisites

- Ensure you have Python interpreter installed. You can download and install Python from the official website: [python.org](https://www.python.org/downloads/).

## Installation

Please install the following packages or libraries 
```
pip install -r requirements.txt
```

## Setting up Project Database
### Setting Your Local Development Environments
1. Create a .env file 
2. Set your local database username and password credentials in the env file
(don't worry its not synced)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://<yourusername>:<yourpassword>@localhost/ticket_hive?charset=utf8mb4&collation=utf8mb4_general_ci'

### Run the Schema insertion script
Run the insertion script
### Running the script
Once everything done, run the 'create_db.py' script to create the models, but you need to create a schema in your mysql host first "ticket_hive"

