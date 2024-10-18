# Project README

## Prerequisites

- Ensure you have Python interpreter installed. You can download and install Python from the official website: [python.org](https://www.python.org/downloads/).

## Installation

Please install the following packages or libraries
1. Flask:
    ```
    pip install Flask
    ```

2. DB lib
    ```
    pip install Flask-SQLAlchemy
    pip install mysqlclient
    pip install mysql-connector-python
    ```

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://<yourusername>:<yourpassword>@localhost/ticket_hive?charset=utf8mb4&collation=utf8mb4_general_ci'

    Once everything done, run the 'create_db.py' script to create the models, but you need to create a schema in your mysql host first "ticket_hive"

