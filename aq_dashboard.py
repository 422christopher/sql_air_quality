"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

# The Flask App instantiation
app = Flask(__name__)

# The API connection
api = openaq.OpenAQ()

# Create the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)


class Record(DB.Model):
    # id (integer, primary key)
    # nullable = False trust that it's implied with primary key
    # BigInteger is only for application has a kazillion users
    id = DB.Column(DB.Integer, primary_key=True)
    # datetime (string)
    datetime = DB.Column(DB.String, nullable=False)
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'At time {self.datetime} the value is {self.value}'


def get_results():
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    aq_list = [(city['date']['utc'], city['value'])
               for city in body['results']]
    return aq_list


@app.route('/')
def root():
    """Base View"""
    # Maybe turn get_results() into a string?
    values_18 = Record.query.filter(Record.value >= 18).all()
    return str(values_18)


@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TO DO Get data from OpenAQ, make Record objects with it, and add to db
    dv_id = 0
    for record in get_results():
        # If there, get it. If not there, make it.
        record_1 = Record(id=dv_id, datetime=str(record[0]), value=record[1])
        DB.session.add(record_1)
        dv_id += 1
    DB.session.commit()
    return 'Data refreshed!'
