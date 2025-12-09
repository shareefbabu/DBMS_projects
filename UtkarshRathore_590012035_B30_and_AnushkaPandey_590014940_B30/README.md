# Pawphoria

## Setup (Windows)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

## Database
mysql -u root -p
SOURCE schema.sql;

Copy .env.example to .env and fill DB credentials.

## Run
set FLASK_APP=app.py
flask run
